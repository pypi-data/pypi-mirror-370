from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

from proalgotrader_core.token_managers.base_token_manager import BaseTokenManager


class AngelOneTokenManager(BaseTokenManager):
    def __init__(
        self,
        username: str,
        totp_key: str,
        mpin: str,
        api_key: str,
        api_secret: str,
        redirect_url: str,
    ) -> None:
        self.username = username
        self.totp_key = totp_key
        self.mpin = mpin
        self.api_key = api_key
        self.api_secret = api_secret
        self.redirect_url = redirect_url

        self.token: str | None = None
        self.session = None
        self.http_client = None
        self.ws_client = None

    async def initialize(self, token: str, feed_token: str | None) -> None:
        self.token = token
        self.feed_token = feed_token

        self.http_client = await self.get_http_client()
        self.ws_client = await self.get_ws_client()

    async def get_http_client(self) -> SmartConnect:
        try:
            http_client = SmartConnect(self.api_key, timeout=5)

            self.session = http_client.generateSession(
                self.username,
                self.mpin,
                await self.get_totp(self.totp_key),
            )

            return http_client
        except Exception as e:
            print(e)

    async def get_ws_client(self) -> SmartWebSocketV2:
        try:
            ws_client = SmartWebSocketV2(
                self.token,
                self.api_key,
                self.username,
                self.feed_token,
            )

            return ws_client
        except Exception as e:
            print(e)
