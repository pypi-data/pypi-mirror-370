import asyncio
import threading

from abc import ABC
from datetime import datetime, timedelta
from typing import List

from logzero import logger

from fyers_apiv3.FyersWebsocket.data_ws import FyersDataSocket
from fyers_apiv3.fyersModel import FyersModel
from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.bar import Bar
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.data_managers.base_data_manager import BaseDataManager
from proalgotrader_core.token_managers.fyers_token_manager import FyersTokenManager


class FyersDataManager(BaseDataManager, ABC):
    def __init__(self, api: Api, algo_session: AlgoSession) -> None:
        self.api = api
        self.algo_session = algo_session

        self.order_broker_info = self.algo_session.project.order_broker_info
        self.broker_config = self.order_broker_info.broker_config

        logger.info("FyersDataManager: getting token manager")

        self.token_manager = FyersTokenManager(
            username=self.broker_config["username"],
            totp_key=self.broker_config["totp_key"],
            pin=self.broker_config["pin"],
            api_key=self.broker_config["api_key"],
            secret_key=self.broker_config["api_secret"],
            redirect_url=self.broker_config["redirect_url"],
        )

        self.http_client: FyersModel | None = None
        self.ws_client: FyersDataSocket | None = None
        self.ws_connected = False

        self.resolutions = {
            timedelta(minutes=1): "ONE_MINUTE",
            timedelta(minutes=3): "THREE_MINUTE",
            timedelta(minutes=5): "FIVE_MINUTE",
            timedelta(minutes=15): "FIFTEEN_MINUTE",
            timedelta(minutes=30): "THIRTY_MINUTE",
            timedelta(hours=1): "ONE_HOUR",
            timedelta(hours=2): "TWO_HOUR",
            timedelta(hours=3): "THREE_HOUR",
            timedelta(hours=4): "FOUR_HOUR",
            timedelta(days=1): "ONE_DAY",
        }

        self.subscribers: List[BrokerSymbol] = []

    async def initialize(self):
        await self.token_manager.initialize(
            token=self.algo_session.broker_token_info["token"],
            feed_token=self.algo_session.broker_token_info["feed_token"],
        )

        self.http_client = self.token_manager.http_client
        self.ws_client = self.token_manager.ws_client

    async def stop_connection(self):
        if self.ws_client:
            self.ws_client.close_connection()

        self.ws_connected = False

    async def start_connection(self):
        try:
            if not self.ws_client:
                logger.info("WebSocket client not initialized")
                return

            logger.info("Setting up WebSocket callbacks...")

            self.ws_client.on_open = self.on_open
            self.ws_client.on_close = self.on_close
            self.ws_client.On_error = self.on_error
            self.ws_client.On_message = self.on_data

            logger.info("Starting WebSocket connection in background thread...")

            connection_thread = threading.Thread(
                target=self.ws_client.connect, daemon=True
            )

            connection_thread.start()

        except Exception as e:
            logger.info(f"Error starting connection: {e}")

    async def on_open(self, wsapp):
        logger.info("✅ WebSocket connection opened successfully")
        self.ws_connected = True

    async def on_close(self, wsapp):
        logger.info("❌ WebSocket connection closed")
        self.ws_connected = False

    async def on_error(self, wsapp, error):
        logger.info(f"❌ WebSocket error: {error}")
        self.ws_connected = False

    async def on_data(self, wsapp, message):
        try:
            if message.get("type") not in ["if", "sf"]:
                return

            for subscriber in self.subscribers:
                if subscriber.symbol_token == message["symbol"]:
                    ltp = message.get("ltp", 0)
                    total_volume = message.get("vol_traded_today", 0)

                    asyncio.run_coroutine_threadsafe(
                        coro=subscriber.on_tick(ltp, total_volume),
                        loop=self.algo_session.algorithm.loop,
                    )
        except Exception as e:
            logger.debug(e)

    async def subscribe(self, broker_symbol: BrokerSymbol) -> None:
        if not self.ws_client:
            logger.info("WebSocket client not initialized; skipping live subscribe")
            return

        try:
            self.ws_client.subscribe(
                symbols=[broker_symbol.symbol_token], data_type="SymbolUpdate"
            )

            self.subscribers.append(broker_symbol)

            logger.info(f"subscribed to {broker_symbol.symbol_name}")

            broker_symbol.subscribed = True
        except Exception as e:
            logger.info(f"Subscribe failed: {e}")

    async def fetch_quotes(self, broker_symbol: BrokerSymbol) -> None:
        try:
            logger.debug(f"fetching quotes {broker_symbol.symbol_token}")

            if not self.http_client:
                logger.info("HTTP client not initialized; cannot fetch quotes")
                return

            payload = {"symbols": broker_symbol.symbol_token}

            response = self.http_client.quotes(data=payload)

            if "d" not in response:
                raise Exception("Error fetching quotes")

            data = response["d"][0]["v"]
            ltp = data.get("lp")
            total_volume = data.get("volume")

            await broker_symbol.on_bar(ltp, total_volume)
        except Exception as e:
            raise Exception(e)

    async def fetch_bars(
        self,
        broker_symbol: BrokerSymbol,
        timeframe: timedelta,
        fetch_from: datetime,
        fetch_to: datetime,
    ) -> List[Bar]:
        try:
            payload = {
                "symbol": broker_symbol.symbol_token,
                "resolution": self.resolutions[timeframe],
                "date_format": "0",
                "range_from": int(fetch_from.timestamp()),
                "range_to": int(fetch_to.timestamp()),
                "cont_flag": "1",
            }

            if not self.http_client:
                logger.info("HTTP client not initialized; cannot fetch candles")
                return []

            response = self.http_client.history(data=payload)

            if "candles" not in response:
                raise Exception("Error fetching candles")

            bars = [
                Bar(
                    broker_symbol=broker_symbol,
                    timestamp=bar[0],
                    open=bar[1],
                    high=bar[2],
                    low=bar[3],
                    close=bar[4],
                    volume=bar[5],
                )
                for bar in response["candles"]
            ]

            return bars
        except Exception as e:
            raise Exception(e)
