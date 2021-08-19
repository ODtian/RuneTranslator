import logging
import re

import httpx
from lxml import etree

from ..error import TranslateError
from ..utils import async_ts


class Bing:
    class_name = "bing"
    api_url = "https://cn.bing.com/ttranslatev3"
    host_url = "https://cn.bing.com/translator"

    def __init__(self):
        self.query_count = 1

    async def get_host_info(self, client):
        r = await client.get(self.host_url)
        html = r.text
        et = etree.HTML(html)

        iid = et.xpath('//*[@id="rich_tta"]/@data-iid')[0] + "."
        ig = re.compile('IG:"(.*?)"').findall(html)[0]

        result = (
            re.compile("var params_RichTranslateHelper = (.*?);")
            .findall(html)[0][1:-1]
            .split(",")
        )
        tk = {"key": result[0], "token": result[1].strip('"')}
        return iid, ig, tk

    @async_ts
    async def translate(self, from_lang, to_lang, *text):
        query_text = "\n".join(text)

        async with httpx.AsyncClient() as client:
            iid, ig, tk = await self.get_host_info(client)
            params = {
                "isVertical": "1",
                "IG": ig,
                "IID": iid + str(self.query_count),
                "": "",
            }

            data = {
                "fromLang": from_lang,
                "to": to_lang,
                "text": query_text,
                **tk,
            }

            result = (
                await client.post(
                    self.api_url,
                    params=params,
                    data=data,
                )
            ).json()

            self.query_count += 1
            logging.debug(result)

            try:
                return result[0]["translations"][0]["text"].split("\n")
            except Exception as e:
                raise TranslateError() from e


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
