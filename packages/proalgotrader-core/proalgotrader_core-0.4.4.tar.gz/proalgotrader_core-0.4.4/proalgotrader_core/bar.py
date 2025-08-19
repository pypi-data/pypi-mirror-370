from datetime import datetime
from typing import Any, List

from proalgotrader_core.broker_symbol import BrokerSymbol


class Bar:
    def __init__(
        self,
        *,
        broker_symbol: BrokerSymbol,
        timestamp: int,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: int = 0,
    ) -> None:
        dt = datetime.fromtimestamp(timestamp)

        self.current_candle = dt
        self.timestamp = timestamp
        self.datetime = dt
        self.broker_symbol = broker_symbol
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    async def get_item(self) -> List[Any]:
        return [
            self.current_candle,
            self.timestamp,
            self.datetime,
            self.broker_symbol.symbol_name,
            self.open,
            self.high,
            self.low,
            self.close,
            self.volume,
        ]
