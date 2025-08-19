from abc import abstractmethod, ABC
from typing import TYPE_CHECKING, Any, Dict
from proalgotrader_core.protocols.base_data_manager import BaseDataManagerProtocol

if TYPE_CHECKING:
    from proalgotrader_core.algo_session import AlgoSession
    from proalgotrader_core.api import Api


class BaseOrderBrokerManagerProtocol(ABC):
    @property
    def data_manager(self) -> BaseDataManagerProtocol: ...

    @abstractmethod
    def __init__(self, api: "Api", algo_session: "AlgoSession") -> None: ...

    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def get_broker_symbols(
        self, broker_title: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]: ...
