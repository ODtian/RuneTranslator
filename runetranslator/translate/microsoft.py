import httpx
import base64
import time
import json
import logging


class Microsoft:
    api_url = "https://api.cognitive.microsofttranslator.com/translate"
    auth_url = "https://edge.microsoft.com/translate/auth"

    def __init__(self):
        self.token = None
        self.expired_time = 0

    @property
    def token_expired(self):
        return self.expired_time <= int(time.time())

    async def update_token(self, client):
        self.token = (await client.get(self.auth_url)).text
        data = self.token.split(".")[1].encode()
        data += b"=" * (4 - len(data) % 4)
        self.expired_time = json.loads(base64.b64decode(data))["exp"]

    async def translate(self, from_lang, to_lang, *text):
        async with httpx.AsyncClient() as client:
            if self.token_expired:
                await self.update_token(client)

            params = {"from": from_lang, "to": to_lang, "api-version": "3.0"}
            headers = {"Authorization": f"Bearer {self.token}"}
            result = (
                await client.post(
                    self.api_url,
                    params=params,
                    headers=headers,
                    json=[{"Text": t} for t in text],
                )
            ).json()
            logging.debug(result)

            return ["".join(t["text"] for t in ts["translations"]) for ts in result]


if __name__ == "__main__":
    import asyncio

    async def main():
        # text = ("トイレで用を足しますか?",)
        text = (
            "G:、叡リ式、扣bmpー2/2文イ牛ー18ー44%ー5000X4022pxー5754MB ー2021/07/2915:11:03(m)-lmョgeG后55 ←今一@の←↑ーロ日朝Ⅱロロー〇ら//",
            "剣との奴商Ⅳe「100) ",
            "を開幕の町ラノティカ自宅 ",
            "創川ⅵ郞創Ⅲ物ⅲ増第郞翡 朝郞ⅵ郞朝 ",
            "05月25日(水)9時24分 ト",
            "イレで用を足しますか? ",
            "入る ",
            "入らない",
        )
        x = Microsoft()
        print(await x.translate("ja", "zh-Hans", *text))

    asyncio.run(main())
