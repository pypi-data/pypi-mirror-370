from asyncio import AbstractEventLoop
from proalgotrader_core.algorithm import Algorithm
from logzero import logger


class Application:
    def __init__(self, loop: AbstractEventLoop) -> None:
        self.algorithm = Algorithm(loop)

    async def start(self) -> None:
        logger.debug("booting application")
        await self.algorithm.boot()

        logger.debug("running application")
        await self.algorithm.run()
