from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.protocols.base_data_manager import (
    BaseDataManagerProtocol,
)


class BaseDataManager(BaseDataManagerProtocol):
    def __init__(self, api: Api, algo_session: AlgoSession) -> None:
        self.api = api
        self.algo_session = algo_session
