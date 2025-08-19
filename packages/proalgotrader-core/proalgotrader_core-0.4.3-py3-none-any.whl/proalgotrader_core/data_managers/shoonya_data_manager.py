import threading

from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Dict, List
from logzero import logger

from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.bar import Bar
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.data_managers.base_data_manager import BaseDataManager
from proalgotrader_core.token_managers.shoonya_token_manager import ShoonyaTokenManager


class ShoonyaDataManager(BaseDataManager, ABC):
    def __init__(self, api: Api, algo_session: AlgoSession) -> None:
        self.api = api
        self.algo_session = algo_session

        self.order_broker_info = self.algo_session.project.order_broker_info
        self.broker_config = self.order_broker_info.broker_config

        logger.info("ShoonyaDataManager: getting token manager")

        # Map expected config to token manager signature
        self.token_manager = ShoonyaTokenManager(
            user_id=self.broker_config["user_id"],
            password=self.broker_config["password"],
            totp_key=self.broker_config["totp_key"],
            vendor_code=self.broker_config["vendor_code"],
            api_secret=self.broker_config["api_secret"],
            imei=self.broker_config["imei"],
        )

        # Shoonya NorenApi used both for HTTP and WS
        self.http_client = self.token_manager.api
        self.ws_connected = False

        self.resolutions = {
            timedelta(minutes=1): "1",
            timedelta(minutes=3): "3",
            timedelta(minutes=5): "5",
            timedelta(minutes=15): "15",
            timedelta(minutes=30): "30",
            timedelta(hours=1): "60",
            timedelta(days=1): "D",
        }

        self.subscribers: List[BrokerSymbol] = []

    # --- WebSocket lifecycle ---
    async def start_connection(self):
        try:
            # prepare token asynchronously so api session is valid
            await self.token_manager.set_access_token_file_name(
                path_name="shoonya_token_manager",
                unique_id=self.algo_session.project.order_broker_info.broker_config[
                    "user_id"
                ],
            )
            await self.token_manager.prepare()

            if not self.http_client:
                logger.info("WebSocket client not initialized")
                return

            logger.info("Setting up Shoonya WebSocket callbacks...")

            # NorenApi.start_websocket accepts named callbacks
            def socket_open():
                self.on_open(None)

            def socket_close():
                self.on_close(None)

            def subscribe_callback(message: Dict[str, Any]):
                # Shoonya sends dict for ticks
                self.on_data(None, message)

            logger.info("Starting Shoonya WebSocket in background thread...")
            connection_thread = threading.Thread(
                target=self._connect_websocket,
                kwargs=dict(
                    subscribe_cb=subscribe_callback,
                    open_cb=socket_open,
                    close_cb=socket_close,
                ),
                daemon=True,
            )
            connection_thread.start()
        except Exception as e:
            logger.info(f"Error starting Shoonya connection: {e}")

    def _connect_websocket(self, subscribe_cb, open_cb, close_cb):
        try:
            # Signature: start_websocket(order_update_callback=None, subscribe_callback=None, socket_open_callback=None, socket_close_callback=None)
            self.http_client.start_websocket(
                order_update_callback=None,
                subscribe_callback=subscribe_cb,
                socket_open_callback=open_cb,
                socket_close_callback=close_cb,
            )
        except Exception as e:
            logger.info(f"Error in Shoonya WebSocket thread: {e}")
            self.ws_connected = False

    async def stop_connection(self):
        try:
            if hasattr(self.http_client, "close_websocket"):
                self.http_client.close_websocket()
            self.ws_connected = False
        except Exception as e:
            logger.info(f"Error stopping Shoonya WebSocket: {e}")

    async def on_open(self, wsapp):
        logger.info("✅ Shoonya WebSocket connection opened successfully")
        self.ws_connected = True

    async def on_close(self, wsapp):
        logger.info("❌ Shoonya WebSocket connection closed")
        self.ws_connected = False

    async def on_error(self, wsapp, error):
        logger.info(f"❌ Shoonya WebSocket error: {error}")
        self.ws_connected = False

    async def on_data(self, wsapp, message: Dict[str, Any]):
        try:
            # Shoonya typical tick fields: 'tk' (token), 'lp' (last price), 'v' (volume)
            token = message.get("tk") or message.get("token")
            if not token:
                return

            for subscriber in self.subscribers:
                if str(subscriber.exchange_token) == str(token):
                    raw_ltp = message.get("lp") or message.get("ltp") or 0
                    try:
                        ltp = float(raw_ltp)
                    except Exception:
                        ltp = 0.0
                    total_volume = (
                        message.get("v") or message.get("volume_trade_for_the_day") or 0
                    )
                    await subscriber.on_tick(ltp, int(total_volume or 0))
        except Exception as e:
            logger.debug(e)

    async def subscribe(self, broker_symbol: BrokerSymbol) -> None:
        try:
            # Shoonya expects exchange prefix with token e.g., nse_cm|<token> or nse_fo|<token>
            exchange_prefix = (
                "nse_cm" if broker_symbol.segment_type == "Equity" else "nse_fo"
            )
            token_str = f"{exchange_prefix}|{broker_symbol.exchange_token}"

            if hasattr(self.http_client, "subscribe"):
                self.http_client.subscribe([token_str])

            self.subscribers.append(broker_symbol)
            logger.info(f"subscribed to {broker_symbol.symbol_name}")
            broker_symbol.subscribed = True
        except Exception as e:
            logger.info(f"Shoonya subscribe error: {e}")

    # --- HTTP data ---
    async def fetch_quotes(self, broker_symbol: BrokerSymbol) -> None:
        # Shoonya HTTP quote endpoint varies; use WS-driven ticks primarily.
        # Fallback: set zeroes to avoid blocking flow.
        try:
            broker_symbol.on_bar(0.0, 0)
        except Exception as e:
            raise Exception(e)

    async def fetch_bars(
        self,
        broker_symbol: BrokerSymbol,
        timeframe: timedelta,
        fetch_from: datetime,
        fetch_to: datetime,
    ) -> List[Bar]:
        # Shoonya historical API not wired here; return empty list to keep adapter compliant
        try:
            return []
        except Exception as e:
            raise Exception(e)
