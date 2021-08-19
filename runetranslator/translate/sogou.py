import hashlib
import logging
import uuid

import httpx

from ..error import TranslateError
from ..utils import async_ts


class Sogou:
    class_name = "sogou"
    host_url = "https://fanyi.sogou.com"
    api_url = "https://fanyi.sogou.com/api/transpc/text/result"

    def __init__(self):
        self.cookies = None

    def get_form(self, from_lang, to_lang, query_text):
        sign_text = f"{from_lang}{to_lang}{query_text}109984457"
        sign = hashlib.md5(sign_text.encode()).hexdigest()

        return {
            "from": from_lang,
            "to": to_lang,
            "text": query_text,
            "uuid": str(uuid.uuid4()),
            "s": sign,
            "client": "pc",  # wap
            "fr": "browser_pc",  # browser_wap
            "needQc": "1",
            "exchange": "false",
        }

    @async_ts
    async def translate(self, from_lang, to_lang, *text):
        query_text = "\n".join(text)

        async with httpx.AsyncClient(cookies=self.cookies) as client:
            if not self.cookies:
                await client.get(self.host_url)
                self.cookies = client.cookies

            data = self.get_form(from_lang, to_lang, query_text)
            result = (
                await client.post(
                    self.api_url,
                    data=data,
                )
            ).json()
            logging.debug(result)

            try:
                return result["data"]["translate"]["dit"].split("\n")
            except Exception as e:
                raise TranslateError() from e


if __name__ == "__main__":
    import asyncio

    async def main():
        # text = ("トイレで用を足しますかー?",)
        text = (
            "G:、叡リ式、扣bmpー2/2文イ牛ー18ー44%ー5000X4022pxー5754MB ー2021/07/2915:11:03(m)-lmョgeG后55 ←今一@の←↑ーロ日朝Ⅱロロー〇ら//",
            "剣との奴商Ⅳe「100) ",
            "を開幕の町ラノティカ自宅 ",
            "創川ⅵ郞創Ⅲ物ⅲ増第郞翡 朝郞ⅵ郞朝 ",
            "05月25日(水)9時24分 ト",
            "イレで用を足しますか'-? ",
            "入る ",
            "入らない",
        )
        x = Sogou()
        print(await x.translate("ja", "zh-CHS", *text))

    asyncio.run(main())
