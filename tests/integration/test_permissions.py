"""Integration tests for the project permissions matrix."""

from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient

_PASSWORD = "correct-horse-battery-staple"


def _credentials() -> dict[str, str]:
    suffix = uuid4().hex
    return {
        "email": f"permissions-user-{suffix}@example.com",
        "username": f"permissions_user_{suffix}",
        "password": _PASSWORD,
    }


async def _register(client: AsyncClient) -> tuple[str, str]:
    response = await client.post(
        "/api/v1/auth/register",
        json=_credentials(),
    )
    assert response.status_code == 201
    data = response.json()
    return data["tokens"]["access_token"], data["user"]["id"]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _create_project(client: AsyncClient, token: str) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/projects/",
        headers=_headers(token),
        json={"name": f"Permissions project {uuid4().hex}"},
    )
    assert response.status_code == 201
    return response.json()


async def _invite_member(
    client: AsyncClient,
    token: str,
    project_id: str,
    user_id: str,
    role: str,
) -> None:
    response = await client.post(
        f"/api/v1/projects/{project_id}/members",
        headers=_headers(token),
        json={"user_id": user_id, "role": role},
    )
    assert response.status_code == 201


async def _project_with_roles(client: AsyncClient) -> dict[str, Any]:
    owner_token, owner_id = await _register(client)
    admin_token, admin_id = await _register(client)
    member_token, member_id = await _register(client)
    non_member_token, non_member_id = await _register(client)
    project = await _create_project(client, owner_token)
    project_id = project["id"]

    await _invite_member(client, owner_token, project_id, admin_id, "ADMIN")
    await _invite_member(client, owner_token, project_id, member_id, "MEMBER")

    return {
        "tokens": {
            "owner": owner_token,
            "admin": admin_token,
            "member": member_token,
            "non_member": non_member_token,
        },
        "project_id": project_id,
        "user_ids": {
            "owner": owner_id,
            "admin": admin_id,
            "member": member_id,
            "non_member": non_member_id,
        },
    }


@pytest.mark.parametrize(
    "actor,action,expected",
    [
        ("owner", "update_project", 200),
        ("admin", "update_project", 200),
        ("member", "update_project", 403),
        ("non_member", "update_project", 404),
        ("owner", "list_members", 200),
        ("admin", "list_members", 200),
        ("member", "list_members", 200),
        ("non_member", "list_members", 404),
        ("owner", "add_member", 201),
        ("admin", "add_member", 201),
        ("member", "add_member", 403),
        ("non_member", "add_member", 404),
        ("owner", "remove_member", 204),
        ("admin", "remove_member", 204),
        ("member", "remove_member", 403),
        ("non_member", "remove_member", 404),
        ("owner", "transfer", 204),
        ("admin", "transfer", 403),
        ("member", "transfer", 403),
        ("non_member", "transfer", 404),
        ("owner", "delete_project", 204),
        ("admin", "delete_project", 403),
        ("member", "delete_project", 403),
        ("non_member", "delete_project", 404),
    ],
)
@pytest.mark.asyncio
async def test_permissions_matrix(
    client: AsyncClient,
    actor: str,
    action: str,
    expected: int,
) -> None:
    """Verify project permissions for every role and protected action."""
    setup = await _project_with_roles(client)
    token = setup["tokens"][actor]
    project_id = setup["project_id"]
    user_ids = setup["user_ids"]
    headers = _headers(token)

    if action == "update_project":
        response = await client.patch(
            f"/api/v1/projects/{project_id}",
            headers=headers,
            json={"name": f"Updated {uuid4().hex}"},
        )
    elif action == "list_members":
        response = await client.get(
            f"/api/v1/projects/{project_id}/members",
            headers=headers,
        )
    elif action == "add_member":
        _, target_id = await _register(client)
        response = await client.post(
            f"/api/v1/projects/{project_id}/members",
            headers=headers,
            json={"user_id": target_id, "role": "MEMBER"},
        )
    elif action == "remove_member":
        response = await client.delete(
            f"/api/v1/projects/{project_id}/members/{user_ids['member']}",
            headers=headers,
        )
    elif action == "transfer":
        response = await client.post(
            f"/api/v1/projects/{project_id}/transfer-ownership",
            headers=headers,
            json={"new_owner_id": user_ids["admin"]},
        )
    else:
        response = await client.delete(
            f"/api/v1/projects/{project_id}",
            headers=headers,
        )

    assert response.status_code == expected
