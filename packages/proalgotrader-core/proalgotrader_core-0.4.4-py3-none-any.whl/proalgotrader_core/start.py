import asyncio

from dotenv import load_dotenv
from logzero import logger
from proalgotrader_core.application import Application


def start() -> None:
    try:
        load_dotenv(verbose=True, override=True)

        loop = asyncio.get_event_loop()

        asyncio.set_event_loop(loop)

        app = Application(loop)

        loop.run_until_complete(app.start())

        loop.close()
    except Exception as e:
        logger.exception(e)
