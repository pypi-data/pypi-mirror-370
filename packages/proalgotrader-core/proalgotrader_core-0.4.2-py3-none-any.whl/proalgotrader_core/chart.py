import pandas as pd

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, List

from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.protocols.enums.segment_type import SegmentType

if TYPE_CHECKING:
    from proalgotrader_core.algorithm import Algorithm
    from proalgotrader_core.chart_manager import ChartManager


class Chart:
    def __init__(
        self,
        algorithm: "Algorithm",
        chart_manager: "ChartManager",
        broker_symbol: BrokerSymbol,
        timeframe: timedelta,
    ) -> None:
        # Store constructor inputs only; full setup happens in async initialize()
        self.algorithm = algorithm
        self.chart_manager = chart_manager
        self.broker_symbol = broker_symbol
        self.timeframe = timeframe

        # Defer wiring until initialize()
        self.algo_session = None  # type: ignore[assignment]
        self.order_broker_manager = None  # type: ignore[assignment]

        # DataFrame and columns are initialized during initialize()
        self.__columns = None  # type: ignore[assignment]
        self.__df = None  # type: ignore[assignment]

        # Next candle time computed during initialize()
        self.next_candle_datetime: datetime | None = None

    @property
    def current_candle(self) -> datetime:
        # Synchronous accessor used only for read-only views; async version is awaited in methods
        return self.algo_session.current_datetime  # type: ignore[union-attr]

    @property
    def ltp(self) -> float:
        return self.broker_symbol.ltp

    @property
    def data(self) -> pd.DataFrame:
        # Use current datetime to avoid awaiting within property
        return self.__df[self.__df.index <= self.algo_session.current_datetime]  # type: ignore[union-attr]

    async def initialize(self) -> None:
        # Wire runtime dependencies
        self.algo_session = self.chart_manager.algo_session
        self.order_broker_manager = self.chart_manager.order_broker_manager

        # Initialize schema and empty dataframe
        self.__columns = [
            "current_candle",
            "timestamp",
            "datetime",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]

        self.__df = pd.DataFrame(columns=self.__columns)

        self.fetch_from, self.fetch_to = await self.algo_session.fetch_ranges(
            self.timeframe
        )

        await self.__fetch_bars()

        await self.__set_next_candle_datetime()

    async def __fetch_bars(self) -> None:
        try:
            bars = await self.algorithm.data_manager.fetch_bars(
                broker_symbol=self.broker_symbol,
                timeframe=self.timeframe,
                fetch_from=self.fetch_from,
                fetch_to=self.fetch_to,
            )

            items = [await item.get_item() for item in bars]

            df = await self.__generate_dataframe(items)

            df.index = pd.to_datetime(df.index)

            df.loc[:, "total_volume"] = df.groupby(df.index.date)["volume"].cumsum()

            self.__df = df
        except Exception as e:
            print("error fetching bars")
            raise Exception(e)

    async def __set_next_candle_datetime(self) -> None:
        current_candle = await self.algo_session.get_current_candle(self.timeframe)
        self.next_candle_datetime = current_candle + self.timeframe

    async def __generate_dataframe(self, data: List[List[Any]]) -> pd.DataFrame:
        df = pd.DataFrame(data=data, columns=self.__columns)

        df.set_index(["current_candle"], inplace=True)

        return df

    async def __get_bar_volume(self, total_volume: int) -> int:
        try:
            if self.broker_symbol.segment_type == SegmentType.Equity.value:
                return 0

            previous_bar_volume = self.__df.total_volume[
                self.__df.index >= self.algo_session.market_start_datetime
            ]

            if len(previous_bar_volume) < 2:
                return total_volume

            total_volume_previous_bar: int = previous_bar_volume.iloc[-2]

            return total_volume - total_volume_previous_bar
        except Exception as e:
            raise Exception(e)

    async def is_new_candle(self) -> bool:
        last_tick = self.algo_session.current_datetime > self.next_candle_datetime

        if last_tick:
            self.next_candle_datetime = self.next_candle_datetime + self.timeframe

        return last_tick

    async def next(self) -> None:
        try:
            if not self.broker_symbol.subscribed:
                return

            new_candle = await self.is_new_candle()

            symbol_name = self.broker_symbol.symbol_name

            ltp = self.broker_symbol.ltp

            total_volume = self.broker_symbol.total_volume

            current_candle = await self.algo_session.get_current_candle(self.timeframe)

            self.__df.loc[current_candle, "timestamp"] = (
                self.algo_session.current_timestamp
            )

            self.__df.loc[current_candle, "datetime"] = (
                self.algo_session.current_datetime
            )

            self.__df.loc[current_candle, "symbol"] = symbol_name

            self.__df.loc[current_candle, "open"] = (
                ltp if new_candle else self.__df.open.iloc[-1]
            )

            self.__df.loc[current_candle, "high"] = (
                ltp if new_candle else max(ltp, self.__df.high.iloc[-1])
            )

            self.__df.loc[current_candle, "low"] = (
                ltp if new_candle else min(ltp, self.__df.low.iloc[-1])
            )

            self.__df.loc[current_candle, "close"] = ltp

            self.__df.loc[current_candle, "volume"] = await self.__get_bar_volume(
                total_volume
            )

            self.__df.loc[current_candle, "total_volume"] = total_volume
        except Exception as e:
            raise Exception(e)
