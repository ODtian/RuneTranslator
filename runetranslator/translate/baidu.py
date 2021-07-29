import hashlib
import random

import httpx


class Baidu:
    api_url = "https://api.fanyi.baidu.com/api/trans/vip/translate"

    def __init__(self, app_id, secret_key):
        self.app_id = app_id
        self.secret_key = secret_key

    async def translate(self, from_lang, to_lang, *text):
        salt = str(random.randint(32768, 65536))
        text_joined = "\n".join(text)
        sign = hashlib.md5(
            (self.app_id + text_joined + salt + self.secret_key).encode()
        ).hexdigest()

        params = {
            "appid": self.app_id,
            "q": text_joined,
            "from": from_lang,
            "to": to_lang,
            "salt": salt,
            "sign": sign,
        }

        async with httpx.AsyncClient() as client:
            r = await client.get(self.api_url, params=params)
            return [line["dst"] for line in r.json()["trans_result"]]
