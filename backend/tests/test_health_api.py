import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "GreenVest" in data["message"]
        assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "providers" in data
        assert "climate" in data["providers"]
        assert "soil" in data["providers"]
        assert data["environmental_weights"]["rainfall"] == 0.40
        assert data["environmental_weights"]["temperature"] == 0.35
        assert data["environmental_weights"]["ph"] == 0.25
