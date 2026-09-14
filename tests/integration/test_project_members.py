"""Integration tests for project membership and ownership flows."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

_PASSWORD = "correct-horse-battery-staple"


def _credentials() -> dict[str, str]:
    suffix = uuid4().hex
    return {
        "email": f"member-user-{suffix}@example.com",
        "username": f"member_user_{suffix}",
        "password": _PASSWORD,
    }


async def _register(client: AsyncClient) -> tuple[dict[str, str], str, str]:
    credentials = _credentials()
    response = await client.post("/api/v1/auth/register", json=credentials)
    assert response.status_code == 201
    data = response.json()
    access_token = data["tokens"]["access_token"]
    user_id = data["user"]["id"]
    assert access_token
    assert user_id
    return credentials, access_token, user_id


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


async def _invite_member(
    client: AsyncClient,
    access_token: str,
    project_id: object,
    user_id: str,
    role: str = "MEMBER",
) -> dict[str, object]:
    response = await client.post(
        f"/api/v1/projects/{project_id}/members",
        headers=_headers(access_token),
        json={"user_id": user_id, "role": role},
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_owner_can_invite_member(client: AsyncClient) -> None:
    """An owner can invite a member and see both memberships."""
    _, owner_token, owner_id = await _register(client)
    _, _, member_id = await _register(client)
    project = await _create_project(client, owner_token)

    invited = await _invite_member(client, owner_token, project["id"], member_id)

    assert invited["project_id"] == project["id"]
    assert invited["user_id"] == member_id
    assert invited["role"] == "MEMBER"

    response = await client.get(
        f"/api/v1/projects/{project['id']}/members",
        headers=_headers(owner_token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    memberships = {item["user_id"]: item["role"] for item in data["items"]}
    assert memberships == {owner_id: "OWNER", member_id: "MEMBER"}


@pytest.mark.asyncio
async def test_invited_member_can_access_project(client: AsyncClient) -> None:
    """An invited member can read the project."""
    _, owner_token, _ = await _register(client)
    _, member_token, member_id = await _register(client)
    project = await _create_project(client, owner_token)
    await _invite_member(client, owner_token, project["id"], member_id)

    response = await client.get(
        f"/api/v1/projects/{project['id']}",
        headers=_headers(member_token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project["id"]
    assert data["name"] == project["name"]


@pytest.mark.asyncio
async def test_admin_can_invite_member(client: AsyncClient) -> None:
    """An admin can invite another member."""
    _, owner_token, _ = await _register(client)
    _, admin_token, admin_id = await _register(client)
    _, _, member_id = await _register(client)
    project = await _create_project(client, owner_token)
    await _invite_member(client, owner_token, project["id"], admin_id, role="ADMIN")

    invited = await _invite_member(client, admin_token, project["id"], member_id)

    assert invited["user_id"] == member_id
    assert invited["role"] == "MEMBER"


@pytest.mark.asyncio
async def test_member_cannot_invite(client: AsyncClient) -> None:
    """A regular member cannot invite another user."""
    _, owner_token, _ = await _register(client)
    _, member_token, member_id = await _register(client)
    _, _, invited_id = await _register(client)
    project = await _create_project(client, owner_token)
    await _invite_member(client, owner_token, project["id"], member_id)

    response = await client.post(
        f"/api/v1/projects/{project['id']}/members",
        headers=_headers(member_token),
        json={"user_id": invited_id, "role": "MEMBER"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "You do not have sufficient permissions for this action."
    }


@pytest.mark.asyncio
async def test_non_member_cannot_list_members(client: AsyncClient) -> None:
    """A non-member cannot list project memberships."""
    _, owner_token, _ = await _register(client)
    _, non_member_token, _ = await _register(client)
    project = await _create_project(client, owner_token)

    response = await client.get(
        f"/api/v1/projects/{project['id']}/members",
        headers=_headers(non_member_token),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Project was not found."}


@pytest.mark.asyncio
async def test_owner_can_transfer_ownership(client: AsyncClient) -> None:
    """Ownership transfer changes which member can delete the project."""
    _, owner_token, _ = await _register(client)
    _, new_owner_token, new_owner_id = await _register(client)
    project = await _create_project(client, owner_token)
    await _invite_member(client, owner_token, project["id"], new_owner_id)

    transfer_response = await client.post(
        f"/api/v1/projects/{project['id']}/transfer-ownership",
        headers=_headers(owner_token),
        json={"new_owner_id": new_owner_id},
    )

    assert transfer_response.status_code == 204
    assert transfer_response.content == b""

    owner_delete = await client.delete(
        f"/api/v1/projects/{project['id']}",
        headers=_headers(owner_token),
    )
    assert owner_delete.status_code == 403

    new_owner_delete = await client.delete(
        f"/api/v1/projects/{project['id']}",
        headers=_headers(new_owner_token),
    )
    assert new_owner_delete.status_code == 204
    assert new_owner_delete.content == b""


@pytest.mark.asyncio
async def test_admin_cannot_transfer_ownership(client: AsyncClient) -> None:
    """An admin cannot transfer ownership."""
    _, owner_token, _ = await _register(client)
    _, admin_token, admin_id = await _register(client)
    _, _, target_id = await _register(client)
    project = await _create_project(client, owner_token)
    await _invite_member(client, owner_token, project["id"], admin_id, role="ADMIN")

    response = await client.post(
        f"/api/v1/projects/{project['id']}/transfer-ownership",
        headers=_headers(admin_token),
        json={"new_owner_id": target_id},
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "You do not have sufficient permissions for this action."
    }


@pytest.mark.asyncio
async def test_transfer_to_non_member_rejected(client: AsyncClient) -> None:
    """Ownership cannot transfer to a non-member."""
    _, owner_token, _ = await _register(client)
    _, _, non_member_id = await _register(client)
    project = await _create_project(client, owner_token)

    response = await client.post(
        f"/api/v1/projects/{project['id']}/transfer-ownership",
        headers=_headers(owner_token),
        json={"new_owner_id": non_member_id},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "User is not a project member"}


@pytest.mark.asyncio
async def test_owner_can_remove_member(client: AsyncClient) -> None:
    """An owner can remove a member from the project."""
    _, owner_token, _ = await _register(client)
    _, member_token, member_id = await _register(client)
    project = await _create_project(client, owner_token)
    await _invite_member(client, owner_token, project["id"], member_id)

    remove_response = await client.delete(
        f"/api/v1/projects/{project['id']}/members/{member_id}",
        headers=_headers(owner_token),
    )

    assert remove_response.status_code == 204
    assert remove_response.content == b""

    access_response = await client.get(
        f"/api/v1/projects/{project['id']}",
        headers=_headers(member_token),
    )
    assert access_response.status_code == 404
    assert access_response.json() == {"detail": "Project was not found."}


@pytest.mark.asyncio
async def test_admin_cannot_remove_other_admin(client: AsyncClient) -> None:
    """An admin cannot remove another admin."""
    _, owner_token, _ = await _register(client)
    _, admin_token, admin_id = await _register(client)
    _, _, other_admin_id = await _register(client)
    project = await _create_project(client, owner_token)
    await _invite_member(client, owner_token, project["id"], admin_id, role="ADMIN")
    await _invite_member(
        client,
        owner_token,
        project["id"],
        other_admin_id,
        role="ADMIN",
    )

    response = await client.delete(
        f"/api/v1/projects/{project['id']}/members/{other_admin_id}",
        headers=_headers(admin_token),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "An admin cannot remove another admin."}
