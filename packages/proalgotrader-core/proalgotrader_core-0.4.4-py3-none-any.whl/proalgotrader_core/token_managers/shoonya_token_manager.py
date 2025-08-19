from NorenRestApiPy.NorenApi import NorenApi

from proalgotrader_core.token_managers.base_token_manager import BaseTokenManager


class ShoonyaTokenManager(BaseTokenManager):
    def __init__(
        self,
        user_id: str,
        password: str,
        totp_key: str,
        vendor_code: str,
        api_secret: str,
        imei: str,
    ) -> None:
        super().__init__()

        self.token: str | None = None

        self.user_id = user_id
        self.password = password
        self.totp_key = totp_key
        self.vendor_code = vendor_code
        self.api_secret = api_secret
        self.imei = imei

        self.api = NorenApi(
            host="https://api.shoonya.com/NorenWClientTP/",
            websocket="wss://api.shoonya.com/NorenWSTP/",
        )

    async def initialize(self, token: str, feed_token: str | None) -> None:
        self.token = token
        self.feed_token = feed_token

    async def set_token(self, token: str) -> None:
        try:
            self.token = token

            self.api.set_session(
                userid=self.user_id,
                password=self.password,
                usertoken=self.token,
            )
        except Exception as e:
            raise Exception(e)

    async def get_token(self) -> str:
        try:
            res = self.api.login(
                userid=self.user_id,
                password=self.password,
                twoFA=await self.get_totp(self.totp_key),
                vendor_code=self.vendor_code,
                api_secret=self.api_secret,
                imei=self.imei,
            )

            usertoken: str = res["susertoken"]

            return usertoken
        except Exception as e:
            raise Exception(e)
