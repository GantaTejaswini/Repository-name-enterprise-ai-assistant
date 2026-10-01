import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


DEMO_EMAIL = "demo@company.com"
DEMO_PASSWORD = "password123"


@pytest.mark.asyncio
async def test_login_success():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.post(
            "/api/auth/login",
            json={
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 50


@pytest.mark.asyncio
async def test_login_wrong_password():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.post(
            "/api/auth/login",
            json={
                "email": DEMO_EMAIL,
                "password": "wrong-password",
            },
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.post(
            "/api/auth/login",
            json={
                "email": "unknown@example.com",
                "password": DEMO_PASSWORD,
            },
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_without_token():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.get("/api/models")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        login_response = await client.post(
            "/api/auth/login",
            json={
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD,
            },
        )

        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        response = await client.get(
            "/api/models",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert "models" in data