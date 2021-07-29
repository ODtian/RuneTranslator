import httpx
import re
import time
import random
import hashlib


class Youdao:
    host_url = "https://fanyi.youdao.com"
    api_url = "https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule"
    headers = {
        "Origin": host_url,
        "Referer": host_url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    }

    sign_re = re.compile(r'n.md5\("fanyideskweb"\+e\+i\+"(.*?)"\)')
    get_sign_re = re.compile(
        "https://shared.ydstatic.com/fanyi/newweb/(.*?)/scripts/newweb/fanyi.min.js"
    )

    def __init__(self):
        self.get_new_sign_url = None
        self.query_count = 0

    async def get_sign_key(self, client):
        if not self.get_new_sign_url:
            host_html = (await client.get(self.host_url)).text
            self.get_new_sign_url = self.get_sign_re.search(host_html).group(0)

        sign_html = (await client.get(self.get_new_sign_url)).text
        sign = self.sign_re.findall(sign_html)
        return sign[0] if sign and sign[0] else "Tbh5E8=q6U3EXe+&L[4c@"

    def get_form(self, query_text, from_language, to_language, sign_key):
        ts = str(int(time.time() * 1000))
        salt = ts + str(random.randrange(0, 10))
        sign_text = "".join(("fanyideskweb", query_text, salt, sign_key))
        sign = hashlib.md5(sign_text.encode()).hexdigest()
        bv = hashlib.md5(self.headers["User-Agent"][8:].encode()).hexdigest()

        return {
            "i": query_text,
            "from": from_language,
            "to": to_language,
            "lts": ts,
            "salt": salt,
            "sign": sign,
            "bv": bv,
            "smartresult": "dict",
            "client": "fanyideskweb",
            "doctype": "json",
            "version": "2.1",
            "keyfrom": "fanyi.web",
            "action": "FY_BY_DEFAULT",
        }

    async def translate(self, from_language, to_language, *text):
        query_text = "\n".join(text)

        async with httpx.AsyncClient(headers=self.headers) as client:

            sign_key = await self.get_sign_key(client)

            data = self.get_form(query_text, from_language, to_language, sign_key)
            r = await client.post(self.api_url, data=data)
            result = r.json()

            if result["errorCode"] != 0:
                self.get_new_sign_url = None
                return await self.translate(from_language, to_language, *text)
            else:
                self.query_count += 1
                return ["".join(s["tgt"] for s in r) for r in result["translateResult"]]


if __name__ == "__main__":
    import asyncio

    async def main():
        x = Youdao()
        r = await x.translate(
            "zh-CHS",
            "ja",
            *(
                "在有关人类事务的发展过程中，",
                "当一个民族必须解除其和另一个与之有关的民族之间的政治联系，并在世界各国之间，接受自然法则和自然界的造物主的旨意赋予的独立和平等的地位时，出于对人类舆论的尊重，必须把他们不得不独立的原因予以宣布。",
            ),
        )
        print(r)

    asyncio.run(main())
