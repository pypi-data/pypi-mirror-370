import hashlib
import json
import logging
import time
from decimal import Decimal
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature
import base64

from tortoise import Tortoise, run_async
from tortoise.transactions import in_transaction
from x_model import init_db
from xync_schema.enums import TransactionStatus

from xync_client.loader import TORM
from xync_schema.models import User, Transfer, Cur, Transaction


class TransactionProofSystem:
    def __init__(self, backend_private_key=None):
        """
        Инициализация системы доказательств транзакций

        Args:
            backend_private_key: Приватный ключ бэкенда
        """
        if backend_private_key is None:
            # Генерируем приватный ключ бэкенда (в реальности должен храниться безопасно)
            self.backend_private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024)
        else:
            self.backend_private_key = backend_private_key

        self.backend_public_key = self.backend_private_key.public_key()

    def generate_user_keys(self):
        """
        Генерация ключей для пользователя (для демонстрации)
        """
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024)
        public_key = private_key.public_key()
        return private_key, public_key

    async def create_payment_request(
        self, receiver_id: int, amount: float, ttl_seconds: int = 3600, sender_id: Optional[int] = None
    ) -> Transfer:
        """
        Создание запроса денег получателем

        Args:
            receiver_id: ID получателя
            amount: Запрашиваемая сумма
            ttl_seconds: Время жизни запроса в секундах (по умолчанию 1 час)
            sender_id: ID конкретного отправителя для личных запросов (None для общих)

        Returns:
            PaymentRequest: Объект запроса
        """
        payment_request = await Transfer.create(
            receiver_id=receiver_id, sender_id=sender_id, amount=amount, ttl=ttl_seconds
        )
        return payment_request

    def create_transaction_hash(
        self, sender_id: int, receiver_id: int, amount: Decimal, timestamp: int, request_id: Optional[int] = None
    ) -> bytes:
        """
        Создание хэша транзакции

        Args:
            sender_id: ID отправителя
            receiver_id: ID получателя
            amount: Сумма
            timestamp: Временная метка
            request_id: ID запроса денег (если транзакция по запросу)
        """
        transaction_data = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "amount": str(amount),  # Переводим в строку для консистентности
            "timestamp": timestamp,
        }

        # Если транзакция по запросу, добавляем ID запроса
        if request_id:
            transaction_data["request_id"] = request_id

        # Сериализуем в JSON с сортировкой ключей для консистентности
        transaction_json = json.dumps(transaction_data, sort_keys=True)

        # Создаем SHA-256 хэш
        return hashlib.sha256(transaction_json.encode()).digest()

    def sign_transaction(self, private_key, transaction_hash: bytes) -> bytes:
        """
        Подписание транзакции приватным ключом
        """
        signature = private_key.sign(
            transaction_hash,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return signature

    async def create_proof(
        self,
        sender_id: int,
        receiver_id: int,
        amount: Decimal,
        timestamp: int,
        sender_signature: bytes,
        request_id: Optional[int] = None,
    ) -> bytes:
        """
        Создание доказательства транзакции бэкендом

        Args:
            sender_id: ID отправителя
            receiver_id: ID получателя
            amount: Сумма транзакции
            timestamp: Временная метка транзакции
            sender_signature: Подпись отправителя
            request_id: ID запроса денег (если транзакция по запросу)
        """

        async with in_transaction():
            # Получаем пользователя и проверяем баланс
            sender: User = await User[1]
            if not sender.prv:
                sender.prv, sender.pub = self.generate_user_keys()
                # await sender.save()
            if await sender.balance() < amount:
                raise ValueError("Недостаточный баланс отправителя")

            # Если указан ID запроса - проверяем его валидность
            payment_request = None
            if request_id:
                payment_request = await Transfer.get_or_none(id=request_id, proof__isnull=True)
                if not payment_request:
                    raise ValueError(f"Запрос {request_id} не найден")

                # Проверяем не истёк ли запрос
                if payment_request.is_expired():
                    raise ValueError(f"Запрос {request_id} истёк")

                # Проверяем не был ли уже оплачен
                if payment_request.is_paid:
                    raise ValueError(f"Запрос {request_id} уже оплачен")

                # Проверяем соответствие параметров запросу
                if payment_request.receiver_id != receiver_id:
                    raise ValueError(
                        f"Получатель не соответствует запросу: ожидался {payment_request.receiver_id}, получен {receiver_id}"
                    )

                if payment_request.amount != amount:
                    raise ValueError(
                        f"Сумма не соответствует запросу: ожидалось {payment_request.amount}, получено {amount}"
                    )

                # Проверяем может ли этот отправитель оплатить запрос
                if not payment_request.is_valid_sender(sender_id):
                    raise ValueError(
                        f"Отправитель {sender_id} не может оплатить личный запрос для {payment_request.sender_id}"
                    )

            # Создаем хэш транзакции
            transaction_hash = self.create_transaction_hash(sender_id, receiver_id, amount, timestamp, request_id)

            # Создаем структуру доказательства
            if request_id:
                # Для транзакции по запросу - включаем только ID запроса
                proof_data = {
                    "transaction_hash": base64.b64encode(transaction_hash).decode(),
                    "sender_signature": base64.b64encode(sender_signature).decode(),
                    "request_id": request_id,
                    "timestamp": timestamp,
                }
            else:
                # Для обычной транзакции - включаем все детали
                proof_data = {
                    "transaction_hash": base64.b64encode(transaction_hash).decode(),
                    "sender_signature": base64.b64encode(sender_signature).decode(),
                    "sender_id": sender_id,
                    "receiver_id": receiver_id,
                    "amount": str(amount),
                    "timestamp": timestamp,
                }

            # Сериализуем доказательство
            proof_json = json.dumps(proof_data, sort_keys=True)
            proof_hash = hashlib.sha256(proof_json.encode()).digest()

            # Подписываем доказательство приватным ключом бэкенда
            backend_signature = self.sign_transaction(self.backend_private_key, proof_hash)

            # Финальное доказательство включает данные + подпись бэкенда
            final_proof = {"proof_data": proof_data, "backend_signature": base64.b64encode(backend_signature).decode()}

            proof_bytes = json.dumps(final_proof).encode()

            # Обновляем балансы
            sender.balance -= amount
            await sender.save()

            receiver = await User.get(id=receiver_id)
            receiver.balance += amount
            await receiver.save()

            # Создаем запись транзакции
            if request_id:
                # Транзакция по запросу
                if payment_request.sender_id:
                    # Личный запрос - записываем только request_id
                    await Transfer.create(request_id=request_id, proof=proof_bytes)
                else:
                    # Общий запрос - записываем request_id и sender_id
                    await Transfer.create(sender_id=sender_id, request_id=request_id, proof=proof_bytes)

                # Отмечаем запрос как оплаченный
                payment_request.is_paid = 1
                await payment_request.save()
            else:
                # Прямая транзакция - записываем все поля
                await Transfer.create(sender_id=sender_id, receiver_id=receiver_id, amount=amount, proof=proof_bytes)

            return proof_bytes

    async def verify_proof(self, proof_bytes: bytes, sender_public_key, backend_public_key) -> Dict[str, Any]:
        """
        Проверка доказательства получателем

        Args:
            proof_bytes: Доказательство в байтах
            sender_public_key: Публичный ключ отправителя
            backend_public_key: Публичный ключ бэкенда

        Returns:
            dict: Результат проверки с деталями
        """

        try:
            # Парсим доказательство
            proof = json.loads(proof_bytes.decode())
            proof_data = proof["proof_data"]
            backend_signature = base64.b64decode(proof["backend_signature"])

            # 1. Проверяем подпись бэкенда
            proof_json = json.dumps(proof_data, sort_keys=True)
            proof_hash = hashlib.sha256(proof_json.encode()).digest()

            try:
                backend_public_key.verify(
                    backend_signature,
                    proof_hash,
                    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                    hashes.SHA256(),
                )
            except InvalidSignature:
                return {"valid": False, "error": "Недействительная подпись бэкенда"}

            # 2. Определяем тип транзакции и восстанавливаем детали
            if "request_id" in proof_data:
                # Транзакция по запросу - восстанавливаем детали из запроса
                request_id = proof_data["request_id"]

                payment_request = await Transfer.get_or_none(id=request_id, proof__isnull=True)
                if not payment_request:
                    return {"valid": False, "error": f"Запрос {request_id} не найден"}

                # Для проверки хэша нужен реальный sender_id из БД
                # Ищем транзакцию по request_id чтобы получить sender_id
                transfer = await Transfer.get_or_none(request_id=request_id, proof__isnull=False)
                if not transfer:
                    return {"valid": False, "error": f"Транзакция для запроса {request_id} не найдена"}

                sender_id = transfer.sender_id  # Реальный sender_id из БД
                receiver_id = payment_request.receiver_id
                amount = payment_request.amount

            else:
                # Обычная транзакция - детали в доказательстве
                sender_id = proof_data["sender_id"]
                receiver_id = proof_data["receiver_id"]
                amount = float(proof_data["amount"])
                request_id = None

            # 3. Проверяем подпись отправителя
            transaction_hash = base64.b64decode(proof_data["transaction_hash"])
            sender_signature = base64.b64decode(proof_data["sender_signature"])

            try:
                sender_public_key.verify(
                    sender_signature,
                    transaction_hash,
                    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                    hashes.SHA256(),
                )
            except InvalidSignature:
                return {"valid": False, "error": "Недействительная подпись отправителя"}

            # 4. Проверяем хэш транзакции
            expected_hash = self.create_transaction_hash(
                sender_id, receiver_id, amount, proof_data["timestamp"], request_id
            )

            if transaction_hash != expected_hash:
                return {"valid": False, "error": "Несоответствие хэша транзакции"}

            # Если все проверки пройдены - транзакция валидна
            transaction_details = {
                "receiver_id": receiver_id,
                "amount": amount,
                "timestamp": proof_data["timestamp"],
                "transaction_type": "by_request" if request_id else "direct",
            }

            # Добавляем sender_id только для прямых транзакций (скрываем для транзакций по запросу)
            if not request_id:
                transaction_details["sender_id"] = sender_id

            # Добавляем request_id для транзакций по запросу
            if request_id:
                transaction_details["request_id"] = request_id

            return {"valid": True, "transaction_details": transaction_details}

        except Exception as e:
            return {"valid": False, "error": f"Ошибка при проверке доказательства: {str(e)}"}


# Демонстрация использования
async def demo():
    """Transactions tests"""
    # Инициализация БД
    logging.basicConfig(level=logging.DEBUG)
    _ = await init_db(TORM)

    # Создаем пользователей в БД
    sender: User = await User[1]
    validator: User = await User[2]
    receiver: User = await User[3]
    # Параметры транзакций
    amount = 10050
    rub = await Cur.get(ticker="EUR")
    timestamp = int(time.time())

    # === СЦЕНАРИЙ 1: Прямая транзакция ===
    print(f"Отправитель {sender.id} отправляет {amount}{rub.ticker} получателю {receiver.id}")
    # Пополняем балансы отправителя и потенциального валидатора
    await Transaction.create(amount=10_000_00, cur=rub, ts=timestamp, status=TransactionStatus.valid, receiver=sender)
    await Transaction.create(
        amount=12_000_00, cur=rub, ts=timestamp, status=TransactionStatus.valid, receiver=validator
    )

    trans = await sender.send(amount, rub.id, receiver.id)
    # Валидатор аппрувит транзакцию
    await trans.vld_sign()
    # Получатель проверяет доказательство
    trans.check()

    # === СЦЕНАРИЙ 2: Общий запрос денег ===
    print("\n=== СЦЕНАРИЙ 2: Общий запрос денег ===")
    print(f"Получатель {receiver.id} создает общий запрос на {amount} (от любого отправителя)")

    # Получатель создает общий запрос денег
    req: Transaction = await receiver.req(1050, rub.id)
    print(f"5. Получатель создал общий запрос: ID {req.id}")

    # Отправитель подписывает транзакцию по запросу
    trans_by_req = await validator.send_by_req(req)
    print("6. Отправитель подписал транзакцию по общему запросу")

    # Получатель проверяет доказательство по запросу
    trans_by_req.check()

    # === СЦЕНАРИЙ 3: Личный запрос денег ===
    print("\n=== СЦЕНАРИЙ 3: Личный запрос денег ===")
    print(f"Получатель {receiver.id} создает личный запрос для отправителя {sender.id}")

    # Получатель создает личный запрос денег
    pers_req: Transaction = await receiver.req(30099, rub.id, sender.id)
    print(f"9. Получатель создал личный запрос: ID {pers_req.id} для {sender.id}")

    # Отправитель подписывает транзакцию по личному запросу
    await sender.send_by_req(pers_req)
    # wrong_sender_trans = await validator.send_by_req(pers_req)
    print("10. Отправитель подписал транзакцию по личному запросу")

    # Проверка: повторная оплата запроса
    print("\n12. Попытка повторной оплаты уже оплаченного запроса:")
    try:
        await proof_system.create_proof(
            sender.id, receiver.id, amount, timestamp, personal_sender_signature, personal_request.id
        )
        print("    ❌ Ошибка: бэкенд не должен был создать доказательство")
    except ValueError as e:
        print(f"    ✅ Бэкенд корректно отклонил повторную оплату: {e}")

    # Показываем записи в БД
    print("\n13. Записи в базе данных:")

    all_transfers = await Transfer.filter(proof__isnull=False)
    print(f"    Транзакций в БД: {len(all_transfers)}")
    for transfer in all_transfers:
        print(
            f"    Transfer ID: {transfer.id}, Sender: {transfer.sender_id}, "
            f"Receiver: {transfer.receiver_id}, Amount: {transfer.amount}, "
            f"Request: {transfer.request_id}"
        )

    all_requests = await Transfer.filter(proof__isnull=True).all()
    print(f"    Запросов в БД: {len(all_requests)}")
    for request in all_requests:
        print(
            f"    Request ID: {request.id}, Receiver: {request.receiver_id}, "
            f"Sender: {request.sender_id}, Amount: {request.amount}, "
            f"Paid: {bool(request.is_paid)}"
        )

    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(demo())
