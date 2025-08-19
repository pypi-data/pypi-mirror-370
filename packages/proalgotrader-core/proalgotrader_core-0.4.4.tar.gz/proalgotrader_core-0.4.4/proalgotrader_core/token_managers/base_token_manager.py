import pyotp


class BaseTokenManager:
    async def get_totp(self, totp_key: str) -> str:
        return pyotp.TOTP(totp_key).now()
