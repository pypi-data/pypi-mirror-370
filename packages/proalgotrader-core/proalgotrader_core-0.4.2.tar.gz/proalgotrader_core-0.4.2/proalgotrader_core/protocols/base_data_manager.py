from abc import abstractmethod, ABC
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List
from proalgotrader_core.bar import Bar
from proalgotrader_core.broker_symbol import BrokerSymbol

if TYPE_CHECKING:
    from proalgotrader_core.algo_session import AlgoSession
    from proalgotrader_core.api import Api


class BaseDataManagerProtocol(ABC):
    @abstractmethod
    def __init__(self, api: "Api", algo_session: "AlgoSession") -> None: ...

    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def start_connection(self) -> None: ...

    @abstractmethod
    async def stop_connection(self) -> None: ...

    @abstractmethod
    async def subscribe(self, broker_symbol: BrokerSymbol) -> None: ...

    @abstractmethod
    async def fetch_quotes(self, broker_symbol: BrokerSymbol) -> None: ...

    @abstractmethod
    async def fetch_bars(
        self,
        broker_symbol: BrokerSymbol,
        timeframe: timedelta,
        fetch_from: datetime,
        fetch_to: datetime,
    ) -> List[Bar]: ...
