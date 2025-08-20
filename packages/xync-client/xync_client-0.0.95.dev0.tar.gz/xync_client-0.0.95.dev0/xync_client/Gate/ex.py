import re
import subprocess
from asyncio import run, sleep
from json import loads

import requests
from bs4 import BeautifulSoup, Script
from pyro_client.client.file import FileClient
from x_model import init_db
from xync_schema.models import Ex
from xync_schema import xtype

from xync_client.Abc.Ex import BaseExClient
from xync_client.loader import TOKEN, TORM
from xync_client.Abc.xtype import PmEx, MapOfIdsList
from xync_client.Gate.etype import ad


class ExClient(BaseExClient):
    logo_pre_url = "www.gate.io"

    # Данные для р2р из html Gate.io
    async def c2c_data(self) -> dict:
        await sleep(1)
        # doc = await self._get("/p2p")  # todo: почему не работает? хз
        doc = requests.get("https://www.gate.io/p2p").text
        await sleep(1)
        soup = BeautifulSoup(doc, "html.parser")
        script: Script = soup.find_all("script", string=re.compile("var c2cData"))[0]  # todo: refact: 23-th not stable
        strng = script.get_text().replace("  ", "")
        pattern = r"var c2cData = (\{.*?\})\s+var transLang"
        match = re.search(pattern, strng.replace(",}", "}").replace(",]", "]"), re.DOTALL)
        res = match.group(1)
        with open("res.js", "w") as file:
            file.write(f"const lang_string = a => a;console.log(JSON.stringify({res}))")
        p = subprocess.Popen(["node", "res.js"], stdout=subprocess.PIPE)
        out = p.stdout.read().decode()
        return loads(out)

    # 20: Список всех платежных методов на бирже
    async def pms(self, cur: str = None) -> dict[int | str, PmEx]:
        data = await self.c2c_data()
        return {
            p["pay_type"]: PmEx(exid=p["pay_type"], name=p["pay_name"], logo=p["image"])
            for p in (data["payment_settings"]).values()
        }

    # 21: Список поддерживаемых валют
    async def coins(self) -> dict[xtype.CoinEx]:
        data = await self.c2c_data()
        return {coin: xtype.CoinEx(exid=coin, ticker=coin) for coin in data["cryptoList"]}

    # 22: Списки поддерживаемых платежек по каждой валюте
    async def cur_pms_map(self) -> MapOfIdsList:
        data = await self.c2c_data()
        return data["fait_payment_settings"]

    async def pairs(self) -> MapOfIdsList:
        coins = (await self.coins()).keys()
        curs = (await self.curs()).keys()
        p = {cur: {c for c in coins} for cur in curs}
        return p, p

    # 23: Монеты на Gate
    async def curs(self) -> dict[xtype.CurEx]:
        data = await self.c2c_data()
        return {cur: xtype.CurEx(exid=cur, ticker=cur) for cur in data["fiatList"]}

    # 24: ads
    async def ads(
        self, coin_exid: str, cur_exid: str, is_sell: bool, pm_exids: list[str | int] = None, amount: int = None
    ) -> list[ad.Ad]:
        data = {
            "type": "push_order_list",
            "symbol": f"{coin_exid}_{cur_exid}",
            "big_trade": "0",
            "fiat_amount": amount or "",
            "amount": "",
            "pay_type": pm_exids and ",".join(pm_exids) or "",
            "is_blue": "0",
            "is_crown": "0",
            "is_follow": "0",
            "have_traded": "0",
            "no_query_hide": "0",
            "per_page": "20",
            "push_type": "sell" if is_sell else "buy",
            "sort_type": "1",
            "page": "1",
        }
        ads = requests.post("https://www.gate.com/json_svr/query_push/", data=data)
        return [ad.Ad(id=_ad["uid"], price=_ad["rate"], **_ad) for _ad in ads.json()["push_order"]]


async def main():
    _ = await init_db(TORM, True)
    gt = await Ex.get(name="Gate")
    async with FileClient(TOKEN) as b:
        cl = ExClient(gt, b)
        _ads = await cl.ads("USDT", "RUB", True, ["payeer"], 1000)
        # curs = await cl.curs()
        # await cl.coins()
        pms = await cl.set_pms()
        print(pms)


if __name__ == "__main__":
    run(main())
