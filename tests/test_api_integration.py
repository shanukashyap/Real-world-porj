"""Full-stack checks against running API + Postgres (INTEGRATION_TESTS=1)."""

import os

import pytest
from httpx import ASGITransport, AsyncClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_health_and_auth_flow():
    if os.getenv("INTEGRATION_TESTS", "").lower() not in ("1", "true", "yes"):
        pytest.skip("Set INTEGRATION_TESTS=1 with Postgres up")

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        h = await client.get("/api/v1/health")
        assert h.status_code == 200

        r = await client.post(
            "/api/v1/auth/register",
            json={"username": "pytest_user_x", "password": "LongSecurePass99!"},
        )
        assert r.status_code in (200, 409)

        tok = await client.post(
            "/api/v1/auth/token",
            data={"username": "soc_analyst", "password": "ChangeMeInProduction!"},
        )
        if tok.status_code != 200:
            pytest.skip("Seed user missing — run via Docker Compose first")

        token = tok.json()["access_token"]
        rag = await client.post(
            "/api/v1/rag/ask",
            headers={"Authorization": f"Bearer {token}"},
            json={"question": "What is OWASP API security?"},
        )
        assert rag.status_code == 200
        body = rag.json()
        assert "answer" in body and "sources" in body
