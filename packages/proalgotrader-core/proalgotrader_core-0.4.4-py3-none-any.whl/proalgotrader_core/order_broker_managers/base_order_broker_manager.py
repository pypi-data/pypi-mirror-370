import asyncio

from contextlib import asynccontextmanager
from abc import abstractmethod
from typing import Any, Dict, List, Type
from logzero import logger

from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.base_symbol import BaseSymbol
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.data_managers.angel_one_data_manager import AngelOneDataManager
from proalgotrader_core.data_managers.base_data_manager import BaseDataManager
from proalgotrader_core.data_managers.fyers_data_manager import FyersDataManager
from proalgotrader_core.data_managers.shoonya_data_manager import ShoonyaDataManager
from proalgotrader_core.order import Order
from proalgotrader_core.position import Position
from proalgotrader_core.protocols.base_order_broker_manager import (
    BaseOrderBrokerManagerProtocol,
)
from proalgotrader_core.protocols.enums.position_type import PositionType

data_managers: Dict[str, Any] = {
    "fyers": FyersDataManager,
    "angel-one": AngelOneDataManager,
    "shoonya": ShoonyaDataManager,
}


class BaseOrderBrokerManager(BaseOrderBrokerManagerProtocol):
    def __init__(self, api: Api, algo_session: AlgoSession) -> None:
        self.api = api
        self.algo_session = algo_session
        self.algorithm = algo_session.algorithm
        self.algo_session_broker = algo_session.project.order_broker_info

        self.id = self.algo_session_broker.id
        self.broker_uid = self.algo_session_broker.broker_uid
        self.broker_title = self.algo_session_broker.broker_title
        self.broker_name = self.algo_session_broker.broker_name
        self.broker_config = self.algo_session_broker.broker_config

        self.base_symbols: Dict[str, BaseSymbol] = {}
        self.broker_symbols: Dict[Any, BrokerSymbol] = {}

        self.initial_capital: float = 0
        self.current_capital: float = 0

        self.__orders: List[Order] = []
        self.__positions: List[Position] = []

        self.__data_manager: BaseDataManager | None = None

        self.processing_request: bool = False

        self.__order_lock: asyncio.Lock = asyncio.Lock()

    @property
    def data_manager(self) -> BaseDataManager:
        return self.__data_manager

    @property
    def orders(self) -> List[Order]:
        return self.__orders

    @property
    def positions(self) -> List[Position]:
        return self.__positions

    @property
    def open_positions(self) -> List[Position]:
        return [position for position in self.__positions if position.status == "open"]

    def is_processing(self) -> bool:
        return self.processing_request

    @asynccontextmanager
    async def processing(self):
        await self.__order_lock.acquire()

        self.processing_request = True

        try:
            yield
        finally:
            self.processing_request = False

            self.__order_lock.release()

    async def initialize(self) -> None:
        print("initializing order broker")

        base_symbols = await self.api.get_base_symbols()

        self.base_symbols = {
            base_symbol["key"]: BaseSymbol(base_symbol) for base_symbol in base_symbols
        }

    def get_data_manager(self) -> BaseDataManager:
        if self.__data_manager:
            return self.__data_manager

        data_manager_instance: Type[BaseDataManager] = data_managers[self.broker_title]

        self.__data_manager = data_manager_instance(
            api=self.api,
            algo_session=self.algo_session,
        )

        return self.__data_manager

    async def get_order_info(self, data: Dict[str, Any]) -> Order:
        broker_symbol = await self.get_symbol(data["broker_symbol"])

        order = Order(data, broker_symbol=broker_symbol, algorithm=self.algorithm)

        await order.initialize()

        return order

    async def get_position_info(self, data: Dict[str, Any]) -> Position:
        broker_symbol = await self.get_symbol(data["broker_symbol"])

        position = Position(data, broker_symbol=broker_symbol, algorithm=self.algorithm)

        await position.initialize()

        return position

    async def set_orders(self) -> None:
        try:
            orders = await self.api.get_orders()

            self.__orders = [await self.get_order_info(order) for order in orders]
        except Exception as e:
            logger.info("set_orders: error happened", e)
            raise Exception(e)

    async def set_positions(self) -> None:
        try:
            positions = await self.api.get_positions()

            self.__positions = [
                await self.get_position_info(position) for position in positions
            ]
        except Exception as e:
            logger.info("set_positions: error happened", e)
            raise Exception(e)

    async def on_after_market_closed(self) -> None:
        try:
            for position in self.positions:
                await position.on_after_market_closed()

            await self.data_manager.stop_connection()
        except Exception as e:
            raise Exception(e)

    async def add_equity(
        self,
        *,
        base_symbol: BaseSymbol,
        market_type: str,
        segment_type: str,
    ) -> BrokerSymbol:
        try:
            data = {
                "base_symbol_id": base_symbol.id,
                "exchange": base_symbol.exchange,
                "market_type": market_type,
                "segment_type": segment_type,
                "expiry_period": None,
                "expiry_date": None,
                "strike_price": None,
                "option_type": None,
            }

            broker_symbol = await self.get_symbol(data)

            return broker_symbol
        except Exception as e:
            raise Exception(e)

    async def add_future(
        self,
        *,
        base_symbol: BaseSymbol,
        market_type: str,
        segment_type: str,
        expiry_period: str,
        expiry_date: str,
    ) -> BrokerSymbol:
        try:
            data = {
                "base_symbol_id": base_symbol.id,
                "exchange": base_symbol.exchange,
                "market_type": market_type,
                "segment_type": segment_type,
                "expiry_period": expiry_period,
                "expiry_date": expiry_date,
                "strike_price": None,
                "option_type": None,
            }

            broker_symbol = await self.get_symbol(data)

            return broker_symbol
        except Exception as e:
            raise Exception(e)

    async def add_option(
        self,
        *,
        base_symbol: BaseSymbol,
        market_type: str,
        segment_type: str,
        expiry_period: str,
        expiry_date: str,
        strike_price: int,
        option_type: str,
    ) -> BrokerSymbol:
        try:
            data = {
                "base_symbol_id": base_symbol.id,
                "exchange": base_symbol.exchange,
                "market_type": market_type,
                "segment_type": segment_type,
                "expiry_period": expiry_period,
                "expiry_date": expiry_date,
                "strike_price": strike_price,
                "option_type": option_type,
            }

            broker_symbol = await self.get_symbol(data)

            return broker_symbol
        except Exception as e:
            raise Exception(e)

    async def get_symbol(
        self,
        broker_symbol_info: Dict[str, Any],
    ) -> BrokerSymbol:
        base_symbol_id = broker_symbol_info["base_symbol_id"]
        exchange = broker_symbol_info["exchange"]
        market_type = broker_symbol_info["market_type"]
        segment_type = broker_symbol_info["segment_type"]
        expiry_period = broker_symbol_info["expiry_period"]
        expiry_date = broker_symbol_info["expiry_date"]
        strike_price = broker_symbol_info["strike_price"]
        option_type = broker_symbol_info["option_type"]

        key = (
            base_symbol_id,
            exchange,
            market_type,
            segment_type,
            expiry_period,
            expiry_date,
            strike_price,
            option_type,
        )

        try:
            return self.broker_symbols[key]
        except KeyError:
            payload = {
                "base_symbol_id": base_symbol_id,
                "exchange": exchange,
                "market_type": market_type,
                "segment_type": segment_type,
                "expiry_period": expiry_period,
                "expiry_date": expiry_date,
                "strike_price": strike_price,
                "option_type": option_type,
            }

            if "id" not in broker_symbol_info:
                filtered_base_symbol = next(
                    base_symbol
                    for base_symbol in self.base_symbols.values()
                    if base_symbol.id == base_symbol_id
                )

                if not filtered_base_symbol:
                    raise Exception("Invalid Base Symbol")

                broker_symbol_info = await self.get_broker_symbols(
                    broker_title=self.broker_title,
                    payload=payload,
                )

            broker_symbol = BrokerSymbol(broker_symbol_info, algorithm=self.algorithm)

            await broker_symbol.initialize()

            self.broker_symbols[key] = broker_symbol

            return broker_symbol

    async def get_broker_symbols(
        self, broker_title: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            broker_symbol: Dict[str, Any] = await self.api.get_broker_symbols(
                broker_title=broker_title,
                payload=payload,
            )

            return broker_symbol
        except Exception as e:
            print(e)

    async def get_positions(
        self,
        symbol_name: str,
        market_type: str,
        order_type: str,
        product_type: str,
        position_type: str,
    ) -> List[Position]:
        return [
            position
            for position in self.positions
            if (
                position.broker_symbol.symbol_name == symbol_name
                and position.broker_symbol.market_type == market_type
                and position.order_type == order_type
                and position.product_type == product_type
                and position.position_type == position_type
            )
        ]

    async def enter_position(
        self,
        *,
        broker_symbol: BrokerSymbol,
        quantities: int,
        product_type: str,
        order_type: str,
        position_type: str,
    ) -> None:
        async with self.processing():
            print("enter position")

            payload: Dict[str, Any] = {
                "algo_session_id": self.algo_session.id,
                "broker_symbol_id": broker_symbol.id,
                "product_type": product_type,
                "order_type": order_type,
                "position_type": position_type,
                "quantities": quantities,
                "price": broker_symbol.ltp,
            }

            data = await self.api.enter_position(payload=payload)

            order = Order(
                data["order"],
                broker_symbol=broker_symbol,
                algorithm=self.algorithm,
            )

            self.__orders.append(order)

            await order.initialize()

            position = Position(
                data["position"],
                broker_symbol=broker_symbol,
                algorithm=self.algorithm,
            )

            self.__positions.append(position)

            await position.initialize()

    async def exit_position(
        self,
        position_id: str,
        broker_symbol: BrokerSymbol,
        quantities: int,
        product_type: str,
        order_type: str,
        position_type: str,
    ) -> None:
        async with self.processing():
            print("exiting position")

            payload: Dict[str, Any] = {
                "position_id": position_id,
                "algo_session_id": self.algo_session.id,
                "broker_symbol_id": broker_symbol.id,
                "product_type": product_type,
                "order_type": order_type,
                "position_type": position_type,
                "quantities": quantities,
                "price": broker_symbol.ltp,
            }

            data = await self.api.exit_position(payload)

            order = Order(
                data["order"],
                broker_symbol=broker_symbol,
                algorithm=self.algorithm,
            )

            self.__orders.append(order)

            await order.initialize()

            position = Position(
                data["position"],
                broker_symbol=broker_symbol,
                algorithm=self.algorithm,
            )

            self.__positions.append(position)

            await position.initialize()

    async def next(self) -> None:
        for position in self.open_positions:
            await position.next()

    @abstractmethod
    async def get_product_types(self) -> Dict[Any, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_order_types(self) -> Dict[Any, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_position_types(self) -> Dict[Any, Any]:
        raise NotImplementedError

    @abstractmethod
    async def set_initial_capital(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set_current_capital(self) -> None:
        raise NotImplementedError
