from typing import Any, Dict, Type
from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.order_broker_managers.angel_one_order_broker_manager import (
    AngelOneOrderBrokerManager,
)
from proalgotrader_core.order_broker_managers.base_order_broker_manager import (
    BaseOrderBrokerManager,
)
from proalgotrader_core.order_broker_managers.fyers_order_broker_manager import (
    FyersOrderBrokerManager,
)
from proalgotrader_core.order_broker_managers.paper_order_broker_manager import (
    PaperOrderBrokerManager,
)
from proalgotrader_core.order_broker_managers.shoonya_order_broker_manager import (
    ShoonyaOrderBrokerManager,
)

order_broker_managers: Dict[str, Any] = {
    "paper": PaperOrderBrokerManager,
    "fyers": FyersOrderBrokerManager,
    "angel-one": AngelOneOrderBrokerManager,
    "shoonya": ShoonyaOrderBrokerManager,
}


class OrderBrokerManager:
    @staticmethod
    async def get_instance(api: Api, algo_session: AlgoSession) -> BaseOrderBrokerManager:
        broker_title = (
            "paper"
            if algo_session.mode == "Paper"
            else algo_session.project.order_broker_info.broker_title
        )

        order_manager_instance: Type[BaseOrderBrokerManager] = order_broker_managers[
            broker_title
        ]

        broker: BaseOrderBrokerManager = order_manager_instance(
            api=api, algo_session=algo_session
        )

        return broker
