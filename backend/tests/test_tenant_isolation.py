import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


DEMO_EMAIL = "demo@company.com"
DEMO_PASSWORD = "password123"

TENANT_B_DOCUMENT_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"


@pytest.mark.asyncio
async def test_document_requires_authentication():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/api/documents/")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_document_lookup_cannot_cross_tenant():
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
            f"/api/documents/{TENANT_B_DOCUMENT_ID}",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

    assert response.status_code == 404