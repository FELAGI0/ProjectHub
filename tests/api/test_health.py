"""Tests for the health check API."""

from unittest import mock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_db_session
from app.main import app


@pytest.fixture
def mock_db_session():
    """Override the database session dependency with an async mock."""
    session = mock.AsyncMock()

    async def get_mock_session():
        yield session

    app.dependency_overrides[get_db_session] = get_mock_session
    yield session
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check_returns_ok(mock_db_session) -> None:
    """A reachable database returns an operational health response."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
    mock_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_health_check_returns_degraded_when_database_unavailable(
    mock_db_session,
) -> None:
    """An unavailable database returns a degraded health response."""
    mock_db_session.execute.side_effect = SQLAlchemyError("Database unavailable")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "database": "unavailable"}
