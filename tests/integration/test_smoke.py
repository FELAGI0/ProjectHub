"""Smoke test for integration fixtures."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint_with_real_db(client):
    """Verify container, migrations, and HTTP client work together."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
