"""Integration tests for authentication flows."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

_PASSWORD = "correct-horse-battery-staple"


def _credentials() -> dict[str, str]:
    suffix = uuid4().hex
    return {
        "email": f"user-{suffix}@example.com",
        "username": f"user_{suffix}",
        "password": _PASSWORD,
    }


async def _register(client: AsyncClient) -> tuple[dict[str, str], dict[str, object]]:
    credentials = _credentials()
    response = await client.post("/api/v1/auth/register", json=credentials)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]
    return credentials, data


@pytest.mark.asyncio
async def test_register_login_returns_tokens(client: AsyncClient) -> None:
    """Registration and login return access and refresh tokens."""
    credentials, _ = await _register(client)

    response = await client.post("/api/v1/auth/login", json=credentials)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]


@pytest.mark.asyncio
async def test_register_duplicate_email_rejected(client: AsyncClient) -> None:
    """Registering an existing email returns conflict."""
    credentials, _ = await _register(client)
    duplicate = {**credentials, "username": f"other_{uuid4().hex}"}

    response = await client.post("/api/v1/auth/register", json=duplicate)

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_wrong_password_rejected(client: AsyncClient) -> None:
    """Login with an incorrect password returns unauthorized."""
    credentials, _ = await _register(client)

    response = await client.post(
        "/api/v1/auth/login",
        json={**credentials, "password": "wrong-password-1234"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rotates_token(client: AsyncClient) -> None:
    """Refreshing revokes the old token and issues a new pair."""
    _, data = await _register(client)
    refresh_token_1 = data["tokens"]["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token_1},
    )

    assert response.status_code == 200
    refreshed = response.json()
    refresh_token_2 = refreshed["tokens"]["refresh_token"]
    assert refreshed["tokens"]["access_token"]
    assert refresh_token_2
    assert refresh_token_2 != refresh_token_1

    old_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token_1},
    )
    assert old_response.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(client: AsyncClient) -> None:
    """Logout revokes the refresh token."""
    _, data = await _register(client)
    refresh_token = data["tokens"]["refresh_token"]

    logout_response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_response.status_code == 204
    assert logout_response.content == b""

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 401


@pytest.mark.asyncio
async def test_logout_all_revokes_all_tokens(client: AsyncClient) -> None:
    """Logout-all revokes tokens issued by registration and login."""
    credentials, registered = await _register(client)
    refresh_token_1 = registered["tokens"]["refresh_token"]
    access_token = registered["tokens"]["access_token"]

    login_response = await client.post("/api/v1/auth/login", json=credentials)
    assert login_response.status_code == 200
    refresh_token_2 = login_response.json()["tokens"]["refresh_token"]

    logout_response = await client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_response.status_code == 204
    assert logout_response.content == b""

    for refresh_token in (refresh_token_1, refresh_token_2):
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 401
