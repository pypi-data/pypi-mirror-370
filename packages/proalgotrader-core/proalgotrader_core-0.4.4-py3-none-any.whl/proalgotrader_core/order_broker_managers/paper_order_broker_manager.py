from typing import Dict, Any
from uuid import uuid4

from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.order_broker_managers.base_order_broker_manager import (
    BaseOrderBrokerManager,
)
from proalgotrader_core.order import Order
from proalgotrader_core.position import Position
from proalgotrader_core.protocols.enums.order_type import OrderType
from proalgotrader_core.protocols.enums.position_type import PositionType
from proalgotrader_core.protocols.enums.product_type import ProductType


class PaperOrderBrokerManager(BaseOrderBrokerManager):
    def __init__(self, api: Api, algo_session: AlgoSession) -> None:
        super().__init__(api=api, algo_session=algo_session)

    async def get_order_types(self) -> Dict[Any, Any]:
        return {
            OrderType.LIMIT_ORDER.value: 1,
            1: OrderType.LIMIT_ORDER.value,
            OrderType.MARKET_ORDER.value: 2,
            2: OrderType.MARKET_ORDER.value,
            OrderType.STOP_ORDER.value: 3,
            3: OrderType.STOP_ORDER.value,
            OrderType.STOP_LIMIT_ORDER.value: 4,
            4: OrderType.STOP_LIMIT_ORDER.value,
        }

    async def get_position_types(self) -> Dict[Any, Any]:
        return {
            PositionType.BUY.value: 1,
            1: PositionType.BUY.value,
            PositionType.SELL.value: -1,
            -1: PositionType.SELL.value,
        }

    async def get_product_types(self) -> Dict[Any, Any]:
        return {
            ProductType.MIS.value: "INTRADAY",
            "INTRADAY": ProductType.MIS.value,
            ProductType.NRML.value: "MARGIN",
            "MARGIN": ProductType.NRML.value,
            ProductType.CNC.value: "CNC",
            "CNC": ProductType.CNC.value,
        }

    async def set_initial_capital(self) -> None:
        self.initial_capital = self.algo_session.initial_capital

    async def set_current_capital(self) -> None:
        self.current_capital = await self.get_current_capital()

    async def get_current_capital(self) -> float:
        initial_capital = self.algo_session.initial_capital
        position_pnl = self.algorithm.position_pnl["pnl"]
        used_margin = sum(
            [
                (
                    position.buy_price * position.buy_quantities
                    if position.position_type == "BUY"
                    else position.sell_price * position.sell_quantities
                )
                for position in self.algorithm.positions
            ]
        )

        return (initial_capital + position_pnl) - used_margin
