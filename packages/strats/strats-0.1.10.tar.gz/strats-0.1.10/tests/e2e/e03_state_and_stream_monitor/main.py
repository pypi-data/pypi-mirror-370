import asyncio
from collections.abc import AsyncGenerator
from decimal import Decimal

from prometheus_client import CollectorRegistry

from strats import Data, State, Strats
from strats.model import (
    PricesData,
    PricesMetrics,
    prices_data_to_prices_metrics,
)
from strats.monitor import StreamClient, StreamMonitor

REGISTRY = CollectorRegistry()


class SampleState(State):
    prices = Data(
        data=PricesData(),
        metrics=PricesMetrics(registry=REGISTRY),
        data_to_metrics=prices_data_to_prices_metrics,
    )


class SampleStreamClient(StreamClient):
    async def stream(self) -> AsyncGenerator[PricesData]:
        for i in range(10):
            yield PricesData(
                bid=Decimal("100") + Decimal(i),
                ask=Decimal("101") + Decimal(i),
            )
            await asyncio.sleep(10)


def create_app():
    return Strats(
        state=SampleState(),
        monitors=[
            StreamMonitor(
                data_name="prices",
                client=SampleStreamClient(),
            )
        ],
        registry=REGISTRY,
    ).create_app()
