import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from .main import create_app


@pytest.mark.asyncio
async def test_02_cron_monitor():
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
                "CronMonitor_1": {
                    "is_running": False,
                },
            },
        }
        assert res.status_code == 200
        assert res.json() == expect

        res = await client.post("/monitors/start")
        expect = {
            "is_configured": True,
            "monitors": {
                "CronMonitor_1": {
                    "is_running": True,
                    "started_at": "2025-01-01T12:04:50+09:00",
                },
            },
        }
        assert res.status_code == 200
        assert res.json() == expect

        # monitor の tick を待つ
        await asyncio.sleep(0.5)

        res = await client.post("/monitors/stop")
        expect = {
            "is_configured": True,
            "monitors": {
                "CronMonitor_1": {
                    "is_running": False,
                },
            },
        }
        assert res.status_code == 200
        assert res.json() == expect
