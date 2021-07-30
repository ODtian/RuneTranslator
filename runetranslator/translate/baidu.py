import hashlib
import logging
import random

import httpx

from ..utils import async_ts


class Baidu:
    class_name = "baidu"
    api_url = "https://api.fanyi.baidu.com/api/trans/vip/translate"

    def __init__(self, app_id, secret_key):
        self.app_id = app_id
        self.secret_key = secret_key

    @async_ts
    async def translate(self, from_lang, to_lang, *text):
        query_text = "\n".join(text)

        salt = str(random.randint(32768, 65536))
        sign = hashlib.md5(
            (self.app_id + query_text + salt + self.secret_key).encode()
        ).hexdigest()

        params = {
            "appid": self.app_id,
            "q": query_text,
            "from": from_lang,
            "to": to_lang,
            "salt": salt,
            "sign": sign,
        }

        async with httpx.AsyncClient() as client:
            result = (await client.get(self.api_url, params=params)).json()
            logging.debug(result)
            return [line["dst"] for line in result.json()["trans_result"]]
