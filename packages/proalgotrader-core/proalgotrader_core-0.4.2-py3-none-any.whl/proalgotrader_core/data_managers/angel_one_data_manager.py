import asyncio
import threading

from abc import ABC
from datetime import datetime, timedelta
from typing import List

from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from logzero import logger

from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.bar import Bar
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.data_managers.base_data_manager import BaseDataManager
from proalgotrader_core.token_managers.angel_one_token_manager import (
    AngelOneTokenManager,
)


class AngelOneDataManager(BaseDataManager, ABC):
    def __init__(self, api: Api, algo_session: AlgoSession) -> None:
        self.api = api
        self.algo_session = algo_session

        self.order_broker_info = self.algo_session.project.order_broker_info
        self.broker_config = self.order_broker_info.broker_config

        logger.info("AngelOneDataManager: getting token manager")

        self.token_manager = AngelOneTokenManager(
            username=self.broker_config["username"],
            totp_key=self.broker_config["totp_key"],
            mpin=self.broker_config["pin"],
            api_key=self.broker_config["api_key"],
            api_secret=self.broker_config["api_secret"],
            redirect_url=self.broker_config["redirect_url"],
        )

        self.http_client: SmartConnect = None
        self.ws_client: SmartWebSocketV2 = None
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
            print("starting connection")

            if not self.ws_client:
                logger.info("WebSocket client not initialized")
                return False

            logger.info("Setting up WebSocket callbacks...")

            self.ws_client.on_open = self.on_open
            self.ws_client.on_close = self.on_close
            self.ws_client.on_error = self.on_error
            self.ws_client.on_data = self.on_data

            logger.info("Starting WebSocket connection in background thread...")

            connection_thread = threading.Thread(
                target=self.ws_client.connect, daemon=True
            )

            connection_thread.start()

        except Exception as e:
            logger.info(f"Error starting connection: {e}")

    def on_open(self, wsapp):
        logger.info("✅ WebSocket connection opened successfully")
        self.ws_connected = True

    def on_close(self, wsapp):
        logger.info("❌ WebSocket connection closed")
        self.ws_connected = False

    def on_error(self, wsapp, error):
        logger.info(f"❌ WebSocket error: {error}")
        self.ws_connected = False

    def on_data(self, wsapp, message):
        try:
            for subscriber in self.subscribers:
                if subscriber.exchange_token == int(message.get("token")):
                    ltp = message.get("last_traded_price", 0) / 100
                    total_volume = message.get("volume_trade_for_the_day", 0)

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

        exchange_type = 1 if broker_symbol.segment_type == "Equity" else 2

        try:
            self.ws_client.subscribe(
                correlation_id="abc123",
                mode=2,
                token_list=[
                    {
                        "exchangeType": exchange_type,
                        "tokens": [broker_symbol.exchange_token],
                    }
                ],
            )

            self.subscribers.append(broker_symbol)

            print("subscribed to", broker_symbol.symbol_name)

            broker_symbol.subscribed = True
        except Exception as e:
            logger.info(f"Subscribe failed: {e}")

    async def fetch_quotes(self, broker_symbol: BrokerSymbol) -> None:
        try:
            logger.debug(f"fetching quotes {broker_symbol.symbol_name}")

            if not self.http_client:
                logger.info("HTTP client not initialized; cannot fetch quotes")
                return

            exchangeTokens = {
                "NSE" if broker_symbol.segment_type == "Equity" else "NFO": [
                    broker_symbol.exchange_token
                ]
            }

            response = self.http_client.getMarketData(
                mode="FULL",
                exchangeTokens=exchangeTokens,
            )

            if not response["data"]:
                raise Exception("Error fetching quotes", broker_symbol.symbol_name)

            data = response["data"]["fetched"][0]
            ltp = data.get("ltp")
            total_volume = data.get("tradeVolume")

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
            historicDataParams = {
                "exchange": broker_symbol.base_symbol.exchange,
                "symboltoken": broker_symbol.exchange_token,
                "interval": self.resolutions[timeframe],
                "fromdate": fetch_from.strftime("%Y-%m-%d %H:%M"),
                "todate": fetch_to.strftime("%Y-%m-%d %H:%M"),
            }

            response = self.http_client.getCandleData(
                historicDataParams=historicDataParams
            )

            if not response["status"]:
                raise Exception("Error fetching candles")

            bars = [
                Bar(
                    broker_symbol=broker_symbol,
                    timestamp=int(datetime.fromisoformat(bar[0]).timestamp()),
                    open=bar[1],
                    high=bar[2],
                    low=bar[3],
                    close=bar[4],
                    volume=bar[5],
                )
                for bar in response["data"]
            ]

            return bars
        except Exception as e:
            raise Exception(e)
