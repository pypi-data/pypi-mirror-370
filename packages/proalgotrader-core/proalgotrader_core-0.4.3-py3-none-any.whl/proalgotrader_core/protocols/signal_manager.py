from abc import abstractmethod, ABC
from typing import TYPE_CHECKING

from proalgotrader_core.protocols.enums.symbol_type import SymbolType

if TYPE_CHECKING:
    from proalgotrader_core.algorithm import Algorithm


class SignalManagerProtocol(ABC):
    @abstractmethod
    def __init__(self, symbol_type: SymbolType, algorithm: "Algorithm") -> None: ...

    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def next(self) -> None: ...
