import asyncio
import re

import pytest
from httpx import ASGITransport, AsyncClient

from .main import create_app


@pytest.mark.asyncio
async def test_03_state_and_stream_monitor():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # >> healthz, metrics
        res = await client.get("/healthz")
        assert res.status_code == 200
        assert res.json() == "ok"

        res = await client.get("/metrics")
        assert res.status_code == 200

        # >> strategy
        res = await client.get("/strategy")
        expect = {"is_configured": False, "is_running": False}
        assert res.status_code == 200
        assert res.json() == expect

        res = await client.post("/strategy/start")
        expect = {"detail": "Missing strategy configuration"}
        assert res.status_code == 400
        assert res.json() == expect

        res = await client.post("/strategy/stop")
        expect = {"detail": "Missing strategy configuration"}
        assert res.status_code == 400
        assert res.json() == expect

        # >> monitors
        res = await client.get("/monitors")
        expect = {
            "is_configured": True,
            "monitors": {
                "StreamMonitor_1": {"is_running": False},
            },
        }
        assert res.status_code == 200
        assert res.json() == expect

        res = await client.post("/monitors/start")
        expect = {
            "is_configured": True,
            "monitors": {
                "StreamMonitor_1": {"is_running": True},
            },
        }
        assert res.status_code == 200
        resjson = res.json()
        # 可変な started_at は比較から除外
        resjson["monitors"]["StreamMonitor_1"].pop("started_at", None)
        assert resjson == expect

        # 監視が一度 tick するのを待つ
        await asyncio.sleep(0.5)

        # >> metrics 検証
        res = await client.get("/metrics")
        assert res.status_code == 200
        body = res.text
        assert extract_unlabeled_metric_value(body, "prices_bid") == 100.0
        assert extract_unlabeled_metric_value(body, "prices_ask") == 101.0
        assert extract_unlabeled_metric_value(body, "prices_spread") == 1.0
        assert extract_unlabeled_metric_value(body, "prices_update_count_total") == 1.0

        # >> stop
        res = await client.post("/monitors/stop")
        expect = {
            "is_configured": True,
            "monitors": {
                "StreamMonitor_1": {"is_running": False},
            },
        }
        assert res.status_code == 200
        assert res.json() == expect


def extract_unlabeled_metric_value(body: str, metric_name: str) -> float:
    pattern = rf"^{re.escape(metric_name)} ([0-9.e+-]+)"
    match = re.search(pattern, body, re.MULTILINE)
    if not match:
        raise ValueError(f"Metric {metric_name} not found")
    return float(match.group(1))
