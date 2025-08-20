import asyncio
import logging
import re

import pytest
from httpx import ASGITransport, AsyncClient

from .main import create_app


@pytest.mark.asyncio
async def test_04_strategy_state_stream_monitor(caplog):
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
        expect = {"is_configured": True, "is_running": False}
        assert res.status_code == 200
        assert res.json() == expect

        # >> monitors
        res = await client.get("/monitors")
        expect = {
            "is_configured": True,
            "monitors": {"StreamMonitor_1": {"is_running": False}},
        }
        assert res.status_code == 200
        assert res.json() == expect

        # >> run
        res = await client.post("/strategy/start")
        expect = {"is_configured": True, "is_running": True}
        assert res.status_code == 200
        resjson = res.json()
        resjson.pop("started_at", None)  # 可変のため除外
        assert resjson == expect

        res = await client.post("/monitors/start")
        expect = {
            "is_configured": True,
            "monitors": {"StreamMonitor_1": {"is_running": True}},
        }
        assert res.status_code == 200
        resjson = res.json()
        resjson["monitors"]["StreamMonitor_1"].pop("started_at", None)  # 可変のため除外
        assert resjson == expect

        # ログ検証に備えて INFO を捕捉
        with caplog.at_level(logging.INFO):
            # 監視・ストラテジが 1 チック動くのを待つ
            await asyncio.sleep(0.5)

        # >> check
        res = await client.get("/metrics")
        assert res.status_code == 200
        body = res.text
        assert extract_unlabeled_metric_value(body, "prices_bid") == 100.0
        assert extract_unlabeled_metric_value(body, "prices_ask") == 101.0
        assert extract_unlabeled_metric_value(body, "prices_spread") == 1.0
        assert extract_unlabeled_metric_value(body, "prices_update_count_total") == 1.0

        # stderr 代わりに caplog でログメッセージを確認
        all_msgs = "\n".join(caplog.messages)
        assert "strategy > bid: 100" in all_msgs

        # >> stop
        res = await client.post("/monitors/stop")
        expect = {
            "is_configured": True,
            "monitors": {"StreamMonitor_1": {"is_running": False}},
        }
        assert res.status_code == 200
        assert res.json() == expect

        res = await client.post("/strategy/stop")
        expect = {"is_configured": True, "is_running": False}
        assert res.status_code == 200
        assert res.json() == expect


def extract_unlabeled_metric_value(body: str, metric_name: str) -> float:
    pattern = rf"^{re.escape(metric_name)} ([0-9.e+-]+)"
    match = re.search(pattern, body, re.MULTILINE)
    if not match:
        raise ValueError(f"Metric {metric_name} not found")
    return float(match.group(1))
