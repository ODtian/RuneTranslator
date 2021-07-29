import re

import httpx
from lxml import etree


class Bing:
    class_name = "bing"
    api_url = "https://cn.bing.com/ttranslatev3"
    host_url = "https://cn.bing.com/translator"

    def __init__(self):
        self.query_count = 1
        self.cookies = None
        self.iid = None
        self.ig = None
        self.tk = None

        self.update_host_info()

    def update_host_info(self):
        r = httpx.get(self.host_url)
        self.cookies = r.cookies

        html = r.text
        et = etree.HTML(html)

        self.iid = et.xpath('//*[@id="rich_tta"]/@data-iid')[0] + "."
        self.ig = re.compile('IG:"(.*?)"').findall(html)[0]

        result = (
            re.compile("var params_RichTranslateHelper = (.*?);")
            .findall(html)[0][1:-1]
            .split(",")
        )
        self.tk = {"key": result[0], "token": result[1].strip('"')}

    async def translate(self, from_lang, to_lang, *text):
        params = {
            "isVertical": "1",
            "IG": self.ig,
            "IID": self.iid + str(self.query_count),
            "": "",
        }

        data = {
            "fromLang": from_lang,
            "to": to_lang,
            "text": "\n".join(text),
            **self.tk,
        }

        async with httpx.AsyncClient() as client:
            r = await client.post(
                self.api_url,
                params=params,
                data=data,
                cookies=self.cookies,
            )

            self.query_count += 1

            data = r.json()
            if isinstance(data, dict) and data.get("statusCode") == 400:
                self.update_host_info()
                return await self.translate(from_lang, to_lang, *text)
            else:
                return data[0]["translations"][0]["text"].split("\n")


if __name__ == "__main__":
    import asyncio

    async def main():
        x = Bing()
        r = await x.translate(
            "zh-Hans",
            "ja",
            *(
                "在有关人类事务的发展过程中，",
                "当一个民族必须解除其和另一个与之有关的民族之间的政治联系，并在世界各国之间，接受自然法则和自然界的造物主的旨意赋予的独立和平等的地位时，出于对人类舆论的尊重，必须把他们不得不独立的原因予以宣布。",
            ),
        )
        print(r)

    asyncio.run(main())
