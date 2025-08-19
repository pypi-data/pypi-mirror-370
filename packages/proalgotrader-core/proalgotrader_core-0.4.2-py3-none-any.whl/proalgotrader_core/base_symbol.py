from typing import Literal, Dict, Any


class BaseSymbol:
    def __init__(self, base_symbol_info: Dict[str, Any]):
        self.id: int = base_symbol_info["id"]
        self.exchange: str = base_symbol_info["exchange"]
        self.key: str = base_symbol_info["key"]
        self.value: str = base_symbol_info["value"]
        self.type: str = base_symbol_info["type"]
        self.lot_size: int = base_symbol_info["lot_size"]
        self.strike_size: int = base_symbol_info["strike_size"]
        self.weekly_expiry_day: str | None = base_symbol_info["weekly_expiry_day"]
        self.monthly_expiry_day: str | None = base_symbol_info["monthly_expiry_day"]

    async def get_expiry_day(self, expiry_period: Literal["Weekly", "Monthly"]) -> str:
        if expiry_period == "Weekly" and self.weekly_expiry_day:
            return self.weekly_expiry_day

        if expiry_period == "Monthly" and self.monthly_expiry_day:
            return self.monthly_expiry_day

        return "Thursday"
