"""Tests for rate limiting on auth endpoints."""

from unittest import mock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.auth import get_user_service
from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.factory import create_application


@pytest.fixture
def application():
    app = create_application()
    service = mock.AsyncMock()
    service.login.side_effect = InvalidCredentialsError()
    app.dependency_overrides[get_user_service] = lambda: service
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def application_with_mocked_service():
    app = create_application()
    service = mock.AsyncMock()
    service.register.side_effect = UserAlreadyExistsError("User already exists.")
    app.dependency_overrides[get_user_service] = lambda: service
    yield app
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_rate_limit(application) -> None:
    """6th login attempt from the same IP returns 429."""
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        for _ in range(5):
            await client.post(
                "/api/v1/auth/login",
                json={"email": "wrong@example.com", "password": "wrong-password"},
            )
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "wrong@example.com", "password": "wrong-password"},
        )

    assert response.status_code == 429


@pytest.mark.asyncio
async def test_register_rate_limit(application_with_mocked_service) -> None:
    """4th register attempt from the same IP returns 429."""
    async with AsyncClient(
        transport=ASGITransport(app=application_with_mocked_service),
        base_url="http://test",
    ) as client:
        for i in range(3):
            await client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"user{i}@example.com",
                    "username": f"user{i}",
                    "password": "correct-horse-battery-staple",
                },
            )
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user99@example.com",
                "username": "user99",
                "password": "correct-horse-battery-staple",
            },
        )

    assert response.status_code == 429


@pytest.mark.asyncio
async def test_rate_limit_has_retry_after_header(application) -> None:
    """429 response includes Retry-After header."""
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        for _ in range(6):
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "wrong@example.com", "password": "wrong-password-12345"},
            )

    assert response.status_code == 429
    assert "retry-after" in response.headers
