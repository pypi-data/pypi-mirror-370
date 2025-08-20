import pytest
from httpx import ASGITransport, AsyncClient

from .main import create_app


@pytest.mark.asyncio
async def test_01_minimal():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # >> healthz, metrics
        r = await client.get("/healthz")
        assert r.status_code == 200
        assert r.json() == "ok"

        r = await client.get("/metrics")
        assert r.status_code == 200

        # >> strategy
        r = await client.get("/strategy")
        assert r.status_code == 200
        assert r.json() == {"is_configured": False, "is_running": False}

        r = await client.post("/strategy/start")
        assert r.status_code == 400
        assert r.json() == {"detail": "Missing strategy configuration"}

        r = await client.post("/strategy/stop")
        assert r.status_code == 400
        assert r.json() == {"detail": "Missing strategy configuration"}

        # >> monitors
        r = await client.get("/monitors")
        assert r.status_code == 200
        assert r.json() == {"is_configured": False}

        r = await client.post("/monitors/start")
        assert r.status_code == 400
        assert r.json() == {"detail": "Missing monitors configuration"}

        r = await client.post("/monitors/stop")
        assert r.status_code == 400
        assert r.json() == {"detail": "Missing monitors configuration"}

        # >> clock
        r = await client.get("/clock")
        assert r.status_code == 200
        assert r.json()["is_real"]

        r = await client.post("/clock/start")
        assert r.status_code == 400
        assert r.json() == {"detail": "Clock is not mock"}

        r = await client.post("/clock/stop")
        assert r.status_code == 400
        assert r.json() == {"detail": "Clock is not mock"}
