import importlib
import asyncio

from datetime import date, datetime, time, timedelta
from typing import Any, List, Literal, Optional, Tuple, Type, Dict
from asyncio import AbstractEventLoop, sleep
from logzero import logger

from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.args_manager import ArgsManager
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.chart import Chart
from proalgotrader_core.chart_manager import ChartManager
from proalgotrader_core._helpers.get_strike_price import get_strike_price
from proalgotrader_core.data_managers.base_data_manager import BaseDataManager
from proalgotrader_core.notification_manager import NotificationManager
from proalgotrader_core.order import Order
from proalgotrader_core.order_broker_manager import OrderBrokerManager
from proalgotrader_core.order_broker_managers.base_order_broker_manager import (
    BaseOrderBrokerManager,
)
from proalgotrader_core.position import Position
from proalgotrader_core.protocols.enums.account_type import AccountType
from proalgotrader_core.protocols.enums.market_type import MarketType
from proalgotrader_core.protocols.enums.order_type import OrderType
from proalgotrader_core.protocols.enums.position_type import PositionType
from proalgotrader_core.protocols.enums.segment_type import SegmentType
from proalgotrader_core.protocols.position_manager import PositionManagerProtocol
from proalgotrader_core.protocols.signal_manager import SignalManagerProtocol
from proalgotrader_core.protocols.strategy import StrategyProtocol


class Algorithm:
    def __init__(self, loop: AbstractEventLoop) -> None:
        self.loop = loop

        self.args_manager = None

        self.api = None

        self.algo_session = None

        self.notification_manager = None

        self.order_broker_manager: BaseOrderBrokerManager | None = None

        self.data_manager: BaseDataManager | None = None

        self.chart_manager: ChartManager | None = None

        self.account_type: AccountType = AccountType.CASH_POSITIONAL

        self.strategy: StrategyProtocol | None = None

        self.signal_manager: Type[SignalManagerProtocol] | None = None

        self.position_manager: Type[PositionManagerProtocol] | None = None

        self.interval = timedelta(seconds=1)

    @property
    def orders(self) -> List[Order]:
        return self.order_broker_manager.orders.copy()

    @property
    def positions(self) -> List[Position]:
        return self.order_broker_manager.positions.copy()

    @property
    def open_positions(self) -> List[Position]:
        return self.order_broker_manager.open_positions.copy()

    @property
    def position_pnl(self) -> Dict[str, float]:
        pnl = sum([position.pnl for position in self.order_broker_manager.positions])

        if pnl > 0:
            return {"pnl": pnl, "profit": pnl, "loss": 0}
        else:
            return {"pnl": pnl, "profit": 0, "loss": abs(pnl)}

    @property
    def total_pnl(self) -> Dict[str, float]:
        pnl = self.position_pnl["pnl"] + self.position_pnl["pnl"]
        profit = self.position_pnl["profit"] + self.position_pnl["profit"]
        loss = self.position_pnl["loss"] + self.position_pnl["loss"]

        return {"pnl": pnl, "profit": profit, "loss": loss}

    @property
    def current_datetime(self) -> datetime:
        return self.algo_session.current_datetime

    @property
    def current_date(self) -> date:
        return self.algo_session.current_date

    @property
    def current_time(self) -> time:
        return self.algo_session.current_time

    def set_interval(self, interval: timedelta) -> None:
        self.interval = interval

    def between_time(self, first: time, second: time) -> bool:
        return first < self.current_time < second

    def set_signal_manager(
        self, *, signal_manager: Optional[Type[SignalManagerProtocol]]
    ) -> None:
        if not signal_manager:
            raise Exception("SignalManager is required.")

        self.signal_manager = signal_manager

    def set_position_manager(
        self, *, position_manager: Optional[Type[PositionManagerProtocol]]
    ) -> None:
        if not position_manager:
            raise Exception("PositionManager is required.")

        self.position_manager = position_manager

    def set_account_type(self, *, account_type: AccountType | None) -> None:
        if not isinstance(account_type, AccountType):
            logger.error("Invalid account type")

        self.account_type = account_type

    async def boot(self) -> None:
        try:
            logger.debug("booting algo")

            self.args_manager = ArgsManager()

            self.args_manager.validate_arguments()

            self.api = Api(args_manager=self.args_manager)

            algo_session_info = await self.api.get_algo_session_info()

            self.algo_session = AlgoSession(
                algorithm=self,
                args_manager=self.args_manager,
                algo_session_info=algo_session_info["algo_session"],
                broker_token_info=algo_session_info["broker_token"],
                reverb_info=algo_session_info["reverb"],
            )

            self.notification_manager = NotificationManager(
                algo_session=self.algo_session
            )

            await self.notification_manager.connect()

            self.order_broker_manager = await OrderBrokerManager.get_instance(
                api=self.api,
                algo_session=self.algo_session,
            )

            self.data_manager = self.order_broker_manager.get_data_manager()

            await self.data_manager.initialize()

            self.chart_manager = ChartManager(algorithm=self)

            if self.args_manager.environment == "production":
                await self.algo_session.project.clone_repository(api=self.api)

            await self.algo_session.initialize()

            await self.algo_session.validate_market_status()

            await self.order_broker_manager.initialize()

            await self.data_manager.start_connection()

            await self.set_strategy()
        except Exception as e:
            raise Exception(e)

    async def run(self) -> None:
        try:
            logger.debug("market is opened")

            await self.initialize()

            await self.next()
        except Exception as e:
            raise Exception(e)

    async def initialize(self) -> None:
        try:
            logger.debug("running initialize")

            assert self.strategy is not None, "strategy must not be None"

            await self.order_broker_manager.set_initial_capital()

            await self.order_broker_manager.set_orders()

            await self.order_broker_manager.set_positions()

            await self.order_broker_manager.set_current_capital()

            await self.strategy.initialize()
        except Exception as e:
            raise Exception(e)

    async def next(self) -> None:
        try:
            logger.debug("running next")

            assert self.strategy is not None, "strategy must not be None"

            market_status = await self.algo_session.get_market_status()

            while market_status == "market_opened":
                if self.chart_manager.charts:
                    await self.chart_next()

                if not self.order_broker_manager.is_processing():
                    await self.strategy.next()
                    await self.order_broker_manager.next()

                await sleep(self.interval.seconds)

            if market_status == "after_market_closed":
                await self.order_broker_manager.on_after_market_closed()

                logger.debug("market is closed")
        except Exception as e:
            raise Exception(e)

    async def chart_next(self) -> None:
        try:
            logger.debug("running chart next")

            tasks = []

            for chart in self.chart_manager.charts:
                task = asyncio.create_task(chart.next())
                tasks.append(task)

            await asyncio.gather(*tasks)
        except Exception as e:
            raise Exception(e)

    async def set_strategy(self) -> None:
        try:
            if not self.strategy:
                module = importlib.import_module("project.strategy")

                strategy_class = getattr(module, "Strategy")

                self.strategy = strategy_class(self)
        except Exception as e:
            raise Exception(e)

    async def add_chart(
        self, broker_symbol: BrokerSymbol, timeframe: timedelta
    ) -> Chart:
        try:
            chart = await self.chart_manager.register_chart(
                broker_symbol,
                timeframe,
            )

            return chart
        except Exception as e:
            raise Exception(e)

    async def add_equity(
        self,
        *,
        symbol_type: str,
    ) -> BrokerSymbol:
        try:
            base_symbol = self.order_broker_manager.base_symbols[symbol_type]

            equity_symbol = await self.order_broker_manager.add_equity(
                base_symbol=base_symbol,
                market_type=MarketType.Cash.value,
                segment_type=SegmentType.Equity.value,
            )

            return equity_symbol
        except Exception as e:
            raise Exception(e)

    async def add_future(
        self,
        *,
        symbol_type: str,
        expiry_input: Tuple[Literal["Weekly", "Monthly"], int],
    ) -> BrokerSymbol:
        try:
            if expiry_input[0] != "Monthly":
                raise Exception("Future expiry must be Monthly")

            equity_symbol = await self.add_equity(symbol_type=symbol_type)

            expiry_period, expiry_date = await self.get_expiry(
                equity_symbol, SegmentType.Future.value, expiry_input
            )

            future_symbol = await self.order_broker_manager.add_future(
                base_symbol=equity_symbol.base_symbol,
                market_type=MarketType.Derivative.value,
                segment_type=SegmentType.Future.value,
                expiry_period=expiry_period,
                expiry_date=expiry_date,
            )

            return future_symbol
        except Exception as e:
            raise Exception(e)

    async def add_option(
        self,
        *,
        symbol_type: str,
        expiry_input: Tuple[Literal["Weekly", "Monthly"], int],
        strike_price_input: int,
        option_type: Literal["CE", "PE"],
    ) -> BrokerSymbol:
        try:
            equity_symbol = await self.add_equity(symbol_type=symbol_type)

            expiry_period, expiry_date = await self.get_expiry(
                equity_symbol, SegmentType.Option.value, expiry_input
            )

            strike_price = await get_strike_price(equity_symbol, strike_price_input)

            option_symbol = await self.order_broker_manager.add_option(
                base_symbol=equity_symbol.base_symbol,
                market_type=MarketType.Derivative.value,
                segment_type=SegmentType.Option.value,
                expiry_period=expiry_period,
                expiry_date=expiry_date,
                strike_price=strike_price,
                option_type=option_type,
            )

            return option_symbol
        except Exception as e:
            raise Exception(e)

    async def get_expiry(
        self,
        broker_symbol: BrokerSymbol,
        segment_type: str,
        expiry_input: Tuple[Literal["Weekly", "Monthly"], int],
    ) -> Tuple[str, Any]:
        try:
            expiry_period, expiry_number = expiry_input

            expiry_day = await broker_symbol.base_symbol.get_expiry_day(expiry_period)

            expires = await self.algo_session.get_expires(expiry_period, expiry_day)

            upcoming_expires = expires[
                (expires.index >= self.current_datetime.strftime("%Y-%m-%d"))
            ]

            expiry_date_current = upcoming_expires.index[expiry_number]

            if expiry_period == "Weekly":
                expiry_date_next = upcoming_expires.index[expiry_number + 1]

                if expiry_date_current.month != expiry_date_next.month:
                    expiry_period = "Monthly"

            return expiry_period, expiry_date_current.strftime("%Y-%m-%d")
        except Exception as e:
            raise Exception(e)

    async def buy(self, *, broker_symbol: BrokerSymbol, quantities: int) -> None:
        try:
            await self.__place_order(
                broker_symbol, quantities, PositionType.BUY, OrderType.MARKET_ORDER
            )
        except Exception as e:
            raise Exception(e)

    async def sell(self, *, broker_symbol: BrokerSymbol, quantities: int) -> None:
        try:
            await self.__place_order(
                broker_symbol, quantities, PositionType.SELL, OrderType.MARKET_ORDER
            )
        except Exception as e:
            raise Exception(e)

    async def __place_order(
        self,
        broker_symbol: BrokerSymbol,
        quantities: int,
        position_type: PositionType,
        order_type: OrderType,
    ) -> None:
        market_type, product_type = self.account_type.value

        try:
            if not broker_symbol:
                raise Exception("Symbol is required")

            if not isinstance(broker_symbol, BrokerSymbol):
                raise Exception("Symbol must be instance of BrokerSymbol")

            if not quantities:
                raise Exception("Quantities is required")

            if broker_symbol.market_type != market_type.value:
                raise Exception("Invalid market type")

            if not broker_symbol.can_trade:
                raise Exception("Can not trade in this symbol")

            if (
                self.account_type == AccountType.CASH_POSITIONAL
                and position_type == PositionType.SELL
            ):
                raise Exception("Equity can't be sold")

            if order_type not in OrderType:
                raise Exception("Invalid order type")

            if quantities % broker_symbol.base_symbol.lot_size != 0:
                raise Exception("Invalid quantities")

            logger.debug(
                f"Placing order, Symbol: {broker_symbol.symbol_name} @ {broker_symbol.ltp} - Qty: {quantities}"
            )

            await self.order_broker_manager.enter_position(
                broker_symbol=broker_symbol,
                quantities=quantities,
                product_type=product_type.value,
                order_type=order_type.value,
                position_type=position_type.value,
            )

            await self.order_broker_manager.set_current_capital()
        except Exception as e:
            raise Exception(e)
