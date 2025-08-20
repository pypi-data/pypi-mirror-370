import pytest
from httpx import ASGITransport, AsyncClient

from .main import create_app


@pytest.mark.asyncio
async def test_01_minimal_clock():
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
        expect = {"is_configured": False}
        assert res.status_code == 200
        assert res.json() == expect

        res = await client.post("/monitors/start")
        expect = {"detail": "Missing monitors configuration"}
        assert res.status_code == 400
        assert res.json() == expect

        res = await client.post("/monitors/stop")
        expect = {"detail": "Missing monitors configuration"}
        assert res.status_code == 400
        assert res.json() == expect

        # >> clock
        res = await client.get("/clock")
        expect = {
            "is_real": False,
            "is_running": False,
            "datetime": "2025-01-01T12:00:00+09:00",
        }
        assert res.status_code == 200
        assert res.json() == expect

        res = await client.post("/clock/start")
        expect = {
            "is_real": False,
            "is_running": True,
            "datetime": "2025-01-01T12:00:00+09:00",
        }
        assert res.status_code == 200
        assert res.json() == expect

        res = await client.post("/clock/stop")
        assert res.status_code == 200
        assert not res.json()["is_running"]
