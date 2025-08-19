from datetime import datetime


class Tick:
    def __init__(
        self,
        *,
        timestamp: int,
        ltp: float,
        total_volume: int,
        symbol: str,
    ) -> None:
        dt = datetime.fromtimestamp(timestamp)
        self.timestamp = timestamp
        self.datetime = dt
        self.ltp = ltp
        self.total_volume = total_volume
        self.symbol = symbol
