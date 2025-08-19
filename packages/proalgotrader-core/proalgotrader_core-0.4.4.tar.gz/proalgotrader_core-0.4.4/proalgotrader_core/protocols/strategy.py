from abc import abstractmethod, ABC

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from proalgotrader_core.algorithm import Algorithm


class StrategyProtocol(ABC):
    @abstractmethod
    def __init__(self, algorithm: "Algorithm") -> None: ...

    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def next(self) -> None: ...
