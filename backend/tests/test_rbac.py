import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_models_requires_authentication():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.get("/api/models")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_can_access_models():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        login_response = await client.post(
            "/api/auth/login",
            json={
                "email": "demo@company.com",
                "password": "password123",
            },
        )

        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        response = await client.get(
            "/api/models",
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

    assert response.status_code == 200
    assert "models" in response.json()


@pytest.mark.asyncio
async def test_invalid_token_rejected():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.get(
            "/api/models",
            headers={
                "Authorization": "Bearer invalid-token"
            },
        )

    assert response.status_code == 401