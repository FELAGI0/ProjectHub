"""Integration tests for project lifecycle and access control."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

_PASSWORD = "correct-horse-battery-staple"


def _credentials() -> dict[str, str]:
    suffix = uuid4().hex
    return {
        "email": f"project-user-{suffix}@example.com",
        "username": f"project_user_{suffix}",
        "password": _PASSWORD,
    }


async def _register(client: AsyncClient) -> tuple[dict[str, str], str]:
    credentials = _credentials()
    response = await client.post("/api/v1/auth/register", json=credentials)
    assert response.status_code == 201
    data = response.json()
    access_token = data["tokens"]["access_token"]
    assert access_token
    return credentials, access_token


def _headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


async def _create_project(
    client: AsyncClient,
    access_token: str,
    name: str | None = None,
) -> dict[str, object]:
    response = await client.post(
        "/api/v1/projects/",
        headers=_headers(access_token),
        json={"name": name or f"Project {uuid4().hex}"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_create_project_owner_in_members(client: AsyncClient) -> None:
    """Creating a project creates an OWNER membership for its creator."""
    _, access_token = await _register(client)
    project = await _create_project(client, access_token)

    response = await client.get(
        f"/api/v1/projects/{project['id']}/members",
        headers=_headers(access_token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    member = data["items"][0]
    assert member["project_id"] == project["id"]
    assert member["user_id"] == project["owner_id"]
    assert member["role"] == "OWNER"


@pytest.mark.asyncio
async def test_delete_project_returns_404_on_get(client: AsyncClient) -> None:
    """Deleting a project makes it unavailable to subsequent reads."""
    _, access_token = await _register(client)
    project = await _create_project(client, access_token)
    project_id = project["id"]

    delete_response = await client.delete(
        f"/api/v1/projects/{project_id}",
        headers=_headers(access_token),
    )
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = await client.get(
        f"/api/v1/projects/{project_id}",
        headers=_headers(access_token),
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_non_member_gets_404_on_project_access(client: AsyncClient) -> None:
    """A non-member cannot access another user's project."""
    _, owner_token = await _register(client)
    _, non_member_token = await _register(client)
    project = await _create_project(client, owner_token)

    response = await client.get(
        f"/api/v1/projects/{project['id']}",
        headers=_headers(non_member_token),
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_projects_returns_only_user_projects(client: AsyncClient) -> None:
    """Project listing contains only projects the current user belongs to."""
    _, first_user_token = await _register(client)
    _, second_user_token = await _register(client)
    first_project = await _create_project(client, first_user_token)
    second_project = await _create_project(client, second_user_token)

    response = await client.get(
        "/api/v1/projects/",
        headers=_headers(first_user_token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert [item["id"] for item in data["items"]] == [first_project["id"]]
    assert second_project["id"] not in [item["id"] for item in data["items"]]


@pytest.mark.asyncio
async def test_update_project_requires_admin_or_owner(client: AsyncClient) -> None:
    """An OWNER can update the project name."""
    _, access_token = await _register(client)
    project = await _create_project(client, access_token)
    updated_name = f"Updated {uuid4().hex}"

    response = await client.patch(
        f"/api/v1/projects/{project['id']}",
        headers=_headers(access_token),
        json={"name": updated_name},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project["id"]
    assert data["name"] == updated_name
    assert data["owner_id"] == project["owner_id"]
