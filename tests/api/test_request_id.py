"""Tests for request ID middleware."""

from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.factory import create_application


@pytest.fixture
def application():
    """Create an application without external database dependencies."""
    return create_application(
        Settings(
            postgres_password="test-password",
            jwt_secret_key="test-secret-key-that-is-long-enough",
        )
    )


@pytest.mark.asyncio
async def test_request_id_is_generated_and_valid(application) -> None:
    """Responses include a generated UUID request ID."""
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    assert UUID(response.headers["X-Request-ID"])


@pytest.mark.asyncio
async def test_request_ids_are_unique(application) -> None:
    """Separate requests receive different request IDs."""
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        first = await client.get("/api/v1/openapi.json")
        second = await client.get("/api/v1/openapi.json")

    assert first.headers["X-Request-ID"] != second.headers["X-Request-ID"]


@pytest.mark.asyncio
async def test_request_id_from_header_is_preserved(application) -> None:
    """The middleware preserves a supplied request ID."""
    request_id = "external-request-id"
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/v1/openapi.json", headers={"X-Request-ID": request_id}
        )

    assert response.headers["X-Request-ID"] == request_id
