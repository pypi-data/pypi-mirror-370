from fyers_apiv3.FyersWebsocket.data_ws import FyersDataSocket
from fyers_apiv3.fyersModel import FyersModel

from proalgotrader_core.token_managers.base_token_manager import BaseTokenManager


class FyersTokenManager(BaseTokenManager):
    def __init__(
        self,
        username: str,
        totp_key: str,
        pin: str,
        api_key: str,
        secret_key: str,
        redirect_url: str,
    ) -> None:
        self.username = username
        self.totp_key = totp_key
        self.pin = pin
        self.api_key = api_key
        self.secret_key = secret_key
        self.redirect_url = redirect_url

        self.ws_client: FyersDataSocket | None = None
        self.http_client: FyersModel | None = None
        self.token: str | None = None

    async def initialize(self, token: str, feed_token: str | None) -> None:
        self.token = token
        self.feed_token = feed_token

        self.http_client = FyersModel(
            client_id=self.api_key,
            token=self.token,
        )

        self.ws_client = FyersDataSocket(
            access_token=f"{self.api_key}:{self.token}",
            litemode=False,
            reconnect=True,
        )
