from datetime import timedelta
from typing import TYPE_CHECKING, Dict, List, Tuple

if TYPE_CHECKING:
    from proalgotrader_core.algorithm import Algorithm

from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.chart import Chart


class ChartManager:
    def __init__(self, algorithm: "Algorithm") -> None:
        self.algorithm = algorithm
        self.order_broker_manager = algorithm.order_broker_manager
        self.api = algorithm.api

        self.__charts: Dict[Tuple[str, timedelta], Chart] = {}

    @property
    def algo_session(self):
        # Always reflect the current algo session
        return self.algorithm.algo_session

    @property
    def charts(self) -> List[Chart]:
        return [chart for chart in self.__charts.values()]

    async def get_chart(
        self, broker_symbol: BrokerSymbol, timeframe: timedelta
    ) -> Chart | None:
        try:
            return self.__charts[(broker_symbol.base_symbol.key, timeframe)]
        except KeyError:
            return None

    async def register_chart(
        self, broker_symbol: BrokerSymbol, timeframe: timedelta
    ) -> Chart:
        try:
            exists = await self.get_chart(broker_symbol, timeframe)

            if exists:
                return exists
            else:
                chart = Chart(
                    algorithm=self.algorithm,
                    chart_manager=self,
                    broker_symbol=broker_symbol,
                    timeframe=timeframe,
                )

                self.__charts[(broker_symbol.base_symbol.key, timeframe)] = chart

                await chart.initialize()

                return chart
        except Exception as e:
            raise Exception(e)
