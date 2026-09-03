"""Tests for the authentication and user-profile API endpoints.

Endpoints under test:
  POST /api/v1/auth/register
  POST /api/v1/auth/login
  POST /api/v1/auth/refresh
  GET  /api/v1/users/me

Dependencies are mocked via ``app.dependency_overrides`` so no database is required.
"""

from datetime import UTC, datetime
from unittest import mock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies.auth import get_current_user
from app.api.v1.auth import get_user_service
from app.core.exceptions import (
    AuthenticationRequiredError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.factory import create_application
from app.modules.users.models import User
from app.modules.users.schemas import (
    AuthenticationResponse,
    TokenPairResponse,
    UserResponse,
)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_USER_ID = uuid4()
_NOW = datetime.now(UTC)


def _make_auth_response() -> AuthenticationResponse:
    """Build a valid AuthenticationResponse for use as a mock return value."""
    return AuthenticationResponse(
        user=UserResponse(
            id=_USER_ID,
            email="test@example.com",
            username="testuser",
            is_active=True,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        tokens=TokenPairResponse(
            access_token="fake-access-token",
            refresh_token="fake-refresh-token",
            access_token_expires_in=900,
        ),
    )


def _make_user(
    is_active: bool = True,
    email: str = "test@example.com",
    username: str = "testuser",
) -> User:
    """Build a User ORM instance suitable for dependency mocks."""
    return User(
        id=_USER_ID,
        email=email,
        username=username,
        password_hash="hashed-placeholder",
        is_active=is_active,
        created_at=_NOW,
        updated_at=_NOW,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    """A fresh application instance per test."""
    application = create_application()
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
def client(app):
    """An HTTP client bound to the test application."""
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.fixture
def mock_service(app):
    """Override get_user_service with an AsyncMock and yield the mock.

    Restores original dependencies after the test.
    """
    svc = mock.AsyncMock()
    app.dependency_overrides[get_user_service] = lambda: svc
    yield svc
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Register — POST /api/v1/auth/register
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_success(client, mock_service) -> None:
    """A valid registration returns 201 with the expected response shape."""
    mock_service.register.return_value = _make_auth_response()

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "correct-horse-battery-staple",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["username"] == "testuser"
    assert data["user"]["is_active"] is True
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client, mock_service) -> None:
    """A duplicate email produces a 409 conflict."""
    mock_service.register.side_effect = UserAlreadyExistsError(
        "A user with these details already exists."
    )

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "existing@example.com",
            "username": "newuser",
            "password": "some-secure-password-42",
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "A user with these details already exists."}


@pytest.mark.asyncio
async def test_register_duplicate_username(client, mock_service) -> None:
    """A duplicate username produces a 409 conflict."""
    mock_service.register.side_effect = UserAlreadyExistsError(
        "A user with these details already exists."
    )

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "another@example.com",
            "username": "takenuser",
            "password": "some-secure-password-42",
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "A user with these details already exists."}


# --- validation (no mock needed — Pydantic rejects before the handler) ---


@pytest.mark.asyncio
async def test_register_invalid_email(client) -> None:
    """An email without an @-sign yields a 422 validation error."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "username": "validuser",
            "password": "my-password-thats-long-enough",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_username_too_short(client) -> None:
    """A username with fewer than 3 characters yields a 422."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "username": "ab",
            "password": "my-password-thats-long-enough",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_password_too_short(client) -> None:
    """A password shorter than 12 characters yields a 422."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "username": "validuser",
            "password": "short",
        },
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Login — POST /api/v1/auth/login
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_success(client, mock_service) -> None:
    """A valid login returns 200 with the expected response shape."""
    mock_service.login.return_value = _make_auth_response()

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "correct-horse-battery-staple",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "test@example.com"
    assert "access_token" in data["tokens"]


@pytest.mark.asyncio
async def test_login_wrong_password(client, mock_service) -> None:
    """An incorrect password produces a 401 error."""
    mock_service.login.side_effect = InvalidCredentialsError()

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrong-password-12345678",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password."}


# ---------------------------------------------------------------------------
# Refresh — POST /api/v1/auth/refresh
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_refresh_success(client, mock_service) -> None:
    """A valid refresh token returns 200 with a new token pair."""
    mock_service.refresh.return_value = _make_auth_response()

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "valid-refresh-token-string"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]


@pytest.mark.asyncio
async def test_refresh_invalid_token(client, mock_service) -> None:
    """An invalid or expired refresh token produces a 401 error."""
    mock_service.refresh.side_effect = AuthenticationRequiredError()

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid-or-expired-token"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication is required."}


# ---------------------------------------------------------------------------
# Get current user — GET /api/v1/users/me
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_current_user(app):
    """Override get_current_user to return a valid User object."""
    user = _make_user()
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_me_success(client, mock_current_user) -> None:
    """An authenticated request returns 200 with the user's profile."""
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer fake-access-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_me_no_token(client) -> None:
    """A request without an Authorization header yields 401."""
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication is required."}


def _raise(exc: Exception) -> None:
    """Helper: a callable that always raises."""
    raise exc


@pytest.fixture
def mock_user_not_found(app):
    """Override get_current_user to raise UserNotFoundError."""
    app.dependency_overrides[get_current_user] = lambda: _raise(UserNotFoundError())
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_me_user_not_found(client, mock_user_not_found) -> None:
    """When the token references a deleted user, a 404 is returned."""
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer fake-access-token"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User was not found."}
