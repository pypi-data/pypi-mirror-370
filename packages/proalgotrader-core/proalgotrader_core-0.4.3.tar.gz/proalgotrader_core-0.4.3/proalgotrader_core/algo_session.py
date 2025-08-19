from asyncio import sleep
import json
import pandas as pd
import pytz

from pathlib import Path
from datetime import date, datetime, time, timedelta
from typing import List, Literal, Tuple, Dict, Any, TYPE_CHECKING
from logzero import logger

from proalgotrader_core._helpers.get_data_path import get_data_path
from proalgotrader_core.args_manager import ArgsManager
from proalgotrader_core.project import Project

if TYPE_CHECKING:
    from proalgotrader_core.algorithm import Algorithm


class AlgoSession:
    def __init__(
        self,
        algorithm: "Algorithm",
        args_manager: ArgsManager,
        algo_session_info: Dict[str, Any],
        broker_token_info: Dict[str, Any],
        reverb_info: Dict[str, Any],
    ):
        self.algorithm = algorithm
        self.args_manager = args_manager
        self.algo_session_info = algo_session_info
        self.broker_token_info = broker_token_info
        self.reverb_info = reverb_info

        self.id: int = self.algo_session_info["id"]
        self.key: str = self.algo_session_info["key"]
        self.secret: str = self.algo_session_info["secret"]
        self.mode: Literal["Paper", "Live"] = self.algo_session_info["mode"]
        self.tz: str = self.algo_session_info["tz"]

        self.project_info = self.algo_session_info["project"]
        self.project: Project = Project(self.project_info)

        self.initial_capital: float = 10_00_000
        self.current_capital: float = 10_00_000

        self.tz_info = pytz.timezone(self.tz)

        self.market_start_time = time(9, 15)

        self.market_end_time = time(15, 30)

        self.market_start_datetime = datetime.now(tz=self.tz_info).replace(
            hour=self.market_start_time.hour,
            minute=self.market_start_time.minute,
            second=0,
            microsecond=0,
            tzinfo=None,
        )

        self.pre_market_time = self.market_start_datetime - timedelta(minutes=15)

        self.market_end_datetime = datetime.now(tz=self.tz_info).replace(
            hour=self.market_end_time.hour,
            minute=self.market_end_time.minute,
            second=0,
            microsecond=0,
            tzinfo=None,
        )

        self.resample_days = {
            "Monday": "W-MON",
            "Tuesday": "W-TUE",
            "Wednesday": "W-WED",
            "Thursday": "W-THU",
            "Friday": "W-FRI",
        }

        self.warmup_days = {
            timedelta(minutes=1): 2,
            timedelta(minutes=3): 4,
            timedelta(minutes=5): 6,
            timedelta(minutes=15): 16,
            timedelta(minutes=30): 32,
            timedelta(hours=1): 60,
            timedelta(hours=2): 100,
            timedelta(hours=3): 150,
            timedelta(hours=4): 200,
            timedelta(days=1): 400,
        }

        self.data_path: Path | None = None

        self.trading_days: pd.DataFrame | None = None

    async def initialize(self) -> None:
        # Resolve data path at async init time
        self.data_path = await get_data_path(self.current_datetime)
        self.trading_days = await self.__get_trading_days(self.data_path)

    @property
    def current_datetime(self) -> datetime:
        return datetime.now(tz=self.tz_info).replace(
            microsecond=0,
            tzinfo=None,
        )

    @property
    def current_timestamp(self) -> int:
        return int(self.current_datetime.timestamp())

    @property
    def current_date(self) -> date:
        return self.current_datetime.date()

    @property
    def current_time(self) -> time:
        return self.current_datetime.time()

    async def get_market_status(self) -> str:
        try:
            if (
                self.current_datetime.strftime("%Y-%m-%d")
                not in self.trading_days.index
            ):
                return "trading_closed"

            if self.current_datetime < self.pre_market_time:
                return "before_market_opened"

            if (self.current_datetime >= self.pre_market_time) and (
                self.current_datetime < self.market_start_datetime
            ):
                return "pre_market_opened"

            if self.current_datetime > self.market_end_datetime:
                return "after_market_closed"

            return "market_opened"
        except Exception as e:
            raise Exception(e)

    async def validate_market_status(self) -> None:
        try:
            while True:
                market_status = await self.get_market_status()

                if market_status == "trading_closed":
                    raise Exception("trading is closed")
                elif market_status == "after_market_closed":
                    raise Exception("market is closed")
                elif market_status == "before_market_opened":
                    raise Exception("market is not opened yet")
                elif market_status == "pre_market_opened":
                    logger.info("market will be opened soon")
                    await sleep(1)
                elif market_status == "market_opened":
                    break
                else:
                    raise Exception("Invalid market status")
        except Exception as e:
            raise Exception(e)

    async def get_expires(
        self, expiry_period: Literal["Weekly", "Monthly"], expiry_day: str
    ) -> pd.DataFrame:
        if expiry_period == "Weekly":
            return await self.__get_weekly_expiries(expiry_day)
        else:
            return await self.__get_monthly_expiries(expiry_day)

    async def __get_weekly_expiries(self, expiry_day: str) -> pd.DataFrame:
        file = f"{self.data_path}/Weekly_{expiry_day}.csv"

        try:
            return pd.read_csv(file, index_col="index", parse_dates=True)
        except FileNotFoundError:
            trading_days = self.trading_days.copy()

            weekends = trading_days.resample(self.resample_days[expiry_day]).last()

            weekends.index = weekends["date"]

            weekends.to_csv(file, index_label="index")

        return pd.read_csv(file, index_col="index", parse_dates=True)

    async def __get_monthly_expiries(self, expiry_day: str) -> pd.DataFrame:
        file = f"{self.data_path}/Monthly_{expiry_day}.csv"

        try:
            return pd.read_csv(file, index_col="index", parse_dates=True)
        except FileNotFoundError:
            weekends: pd.DataFrame = await self.__get_weekly_expiries(expiry_day)

            datetime_index: pd.DatetimeIndex = pd.DatetimeIndex(weekends.index)

            df_grouped = weekends.groupby(
                by=[datetime_index.year, datetime_index.month],
                as_index=True,
                dropna=True,
            ).last()

            json_data = json.loads(df_grouped.to_json())

            async def get_data(date: str) -> List[Any]:
                datetime_obj = datetime.fromisoformat(date)

                return [date, datetime_obj.strftime("%A"), datetime_obj.year]

            data = [await get_data(date) for date in json_data["date"].values()]

            new_df = pd.DataFrame(data, columns=["date", "day", "year"])

            new_df["index"] = pd.to_datetime(new_df["date"])

            new_df.set_index("index", inplace=True)

            new_df.to_csv(file, index_label="index")

            return pd.read_csv(file, index_col="index", parse_dates=True)

    async def get_warmups_days(self, timeframe: timedelta) -> int:
        try:
            return self.warmup_days[timeframe]
        except KeyError:
            raise Exception("Invalid timeframe")

    async def fetch_ranges(self, timeframe: timedelta) -> Tuple[datetime, datetime]:
        warmups_days = await self.get_warmups_days(timeframe)

        warmups_from: str = str(
            (
                self.trading_days[
                    self.trading_days.index < self.current_datetime.strftime("%Y-%m-%d")
                ]
                .tail(warmups_days)
                .head(1)
                .index[0]
            )
        )

        fetch_from_epoch = datetime.fromisoformat(warmups_from).replace(
            hour=self.market_start_time.hour,
            minute=self.market_start_time.minute,
            second=self.market_start_time.second,
            microsecond=0,
        )

        return fetch_from_epoch, self.current_datetime

    async def get_current_candle(self, timeframe: timedelta) -> datetime:
        try:
            if timeframe == timedelta(days=1):
                return datetime.now(tz=self.tz_info).replace(
                    hour=5,
                    minute=30,
                    second=0,
                    microsecond=0,
                    tzinfo=None,
                )

            current_candle_timedelta: timedelta = (
                self.current_datetime - self.market_start_datetime
            )

            seconds, _ = divmod(
                int(current_candle_timedelta.seconds), int(timeframe.total_seconds())
            )

            return self.market_start_datetime + timedelta(
                seconds=seconds * timeframe.total_seconds()
            )
        except Exception as e:
            raise Exception(e)

    async def __get_trading_days(self, data_path: Path) -> pd.DataFrame:
        file = f"{data_path}/trading_days.csv"

        try:
            return pd.read_csv(file, index_col="index", parse_dates=["index", "date"])
        except FileNotFoundError:
            trading_days = await self.algorithm.api.get_trading_days()

            def get_json(date: str) -> Dict[str, Any]:
                dt = datetime.strptime(date, "%Y-%m-%d")

                return {
                    "date": dt.strftime("%Y-%m-%d"),
                    "day": dt.strftime("%A"),
                    "year": dt.year,
                }

            df = pd.DataFrame(
                data=[get_json(trading_day["date"]) for trading_day in trading_days],
                columns=["date", "day", "year"],
            )

            df["index"] = pd.to_datetime(df["date"])

            df.set_index(["index"], inplace=True)

            df.to_csv(file, index_label="index")

        return pd.read_csv(file, index_col="index", parse_dates=["index", "date"])
