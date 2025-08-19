from proalgotrader_core.broker_symbol import BrokerSymbol


async def get_strike_price(
    broker_symbol: BrokerSymbol, strike_price_input: int = 0
) -> int:
    try:
        strike_size = broker_symbol.base_symbol.strike_size
        total_increment = strike_size * strike_price_input

        rounded_quotient = round(broker_symbol.ltp / strike_size)
        nearest_denomination = rounded_quotient * strike_size

        return int(nearest_denomination + total_increment)
    except Exception as e:
        raise Exception(e)
