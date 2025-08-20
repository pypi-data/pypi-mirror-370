from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from prometheus_client import REGISTRY, CollectorRegistry, Counter, Gauge


@dataclass
class PricesData:
    bid: Decimal = Decimal("0")
    ask: Decimal = Decimal("0")


class PricesMetrics:
    def __init__(
        self,
        *,
        registry: Optional[CollectorRegistry] = None,
        namespace: Optional[str] = None,
        subsystem: Optional[str] = None,
    ) -> None:
        reg = registry or REGISTRY

        self.bid = Gauge(
            "prices_bid",
            "Bid price.",
            namespace=namespace or "",
            subsystem=subsystem or "",
            registry=reg,
        )
        self.ask = Gauge(
            "prices_ask",
            "Ask price.",
            namespace=namespace or "",
            subsystem=subsystem or "",
            registry=reg,
        )
        self.spread = Gauge(
            "prices_spread",
            "Ask - Bid.",
            namespace=namespace or "",
            subsystem=subsystem or "",
            registry=reg,
        )
        self.update_count_total = Counter(
            "prices_update_count_total",
            "Number of price updates.",
            namespace=namespace or "",
            subsystem=subsystem or "",
            registry=reg,
        )


def prices_data_to_prices_metrics(data: PricesData, metrics: PricesMetrics):
    metrics.bid.set(float(data.bid))
    metrics.ask.set(float(data.ask))
    metrics.spread.set(float(data.ask - data.bid))
    metrics.update_count_total.inc()
