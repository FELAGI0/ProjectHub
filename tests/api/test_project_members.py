"""Tests for the project member management API endpoints.

Endpoints under test:
  GET    /api/v1/projects/{project_id}/members
  POST   /api/v1/projects/{project_id}/members
  PATCH  /api/v1/projects/{project_id}/members/{user_id}
  DELETE /api/v1/projects/{project_id}/members/{user_id}

Dependencies are mocked via `app.dependency_overrides` so no database is required.
"""

from datetime import UTC, datetime
from unittest import mock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies.auth import get_current_user
from app.api.v1.project_members import get_member_service
from app.core.exceptions import (
    InsufficientPermissionError,
    MemberNotFoundError,
    ProjectAccessDeniedError,
    ProjectNotFoundError,
)
from app.factory import create_application
from app.modules.project_members.models import ProjectRole
from app.modules.project_members.schemas import (
    MemberResponse,
    PaginatedMembersResponse,
)
from app.modules.users.models import User

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_OWNER_ID = uuid4()
_PROJECT_ID = uuid4()
_MEMBER_ID = uuid4()
_OTHER_ID = uuid4()
_NOW = datetime.now(UTC)


def _make_member_response(
    user_id=None, role: ProjectRole = ProjectRole.MEMBER
) -> MemberResponse:
    """Build a valid MemberResponse for use as a mock return value."""
    return MemberResponse(
        id=_MEMBER_ID,
        project_id=_PROJECT_ID,
        user_id=user_id or _OWNER_ID,
        role=role,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _paginated_response(
    items: list[MemberResponse] | None = None,
) -> PaginatedMembersResponse:
    """Build a paginated response for use as a mock return value."""
    items = items or [_make_member_response()]
    return PaginatedMembersResponse(
        items=items,
        total=len(items),
        page=1,
        page_size=20,
        total_pages=1,
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
def mock_current_user(app):
    """Override get_current_user to return a valid User object."""
    user = User(
        id=_OWNER_ID,
        email="owner@example.com",
        username="owner",
        password_hash="hashed-placeholder",
        is_active=True,
        created_at=_NOW,
        updated_at=_NOW,
    )
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    app.dependency_overrides.clear()


@pytest.fixture
def mock_service(app):
    """Override get_member_service with an AsyncMock and yield the mock."""
    svc = mock.AsyncMock()
    app.dependency_overrides[get_member_service] = lambda: svc
    yield svc
    app.dependency_overrides.clear()


@pytest.fixture
def mock_no_auth(app):
    """Override get_current_user to raise AuthenticationRequiredError."""
    from app.core.exceptions import AuthenticationRequiredError

    def _raise(exc):
        raise exc

    app.dependency_overrides[get_current_user] = lambda: _raise(
        AuthenticationRequiredError()
    )
    yield
    app.dependency_overrides.clear()
# ---------------------------------------------------------------------------
# List Members -- GET /api/v1/projects/{project_id}/members
# ---------------------------------------------------------------------------


class TestListMembers:
    """GET /projects/{id}/members -- list project members."""

    @pytest.mark.asyncio
    async def test_success(self, client, mock_service, mock_current_user) -> None:
        """Returns 200 with a paginated list of members."""
        mock_service.list_members.return_value = _paginated_response()

        response = await client.get(f"/api/v1/projects/{_PROJECT_ID}/members")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_not_found(self, client, mock_service, mock_current_user) -> None:
        """A non-existent project yields 404."""
        mock_service.list_members.side_effect = ProjectNotFoundError()

        response = await client.get(f"/api/v1/projects/{uuid4()}/members")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_access_denied(self, client, mock_service, mock_current_user) -> None:
        """Caller is not a member yields 403."""
        mock_service.list_members.side_effect = ProjectAccessDeniedError()

        response = await client.get(f"/api/v1/projects/{_PROJECT_ID}/members")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_no_auth(self, client, mock_service, mock_no_auth) -> None:
        """Missing authentication yields a 401 error."""
        response = await client.get(f"/api/v1/projects/{_PROJECT_ID}/members")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_pagination(self, client, mock_service, mock_current_user) -> None:
        """Pagination parameters are forwarded to the service."""
        mock_service.list_members.return_value = _paginated_response(items=[])

        response = await client.get(
            f"/api/v1/projects/{_PROJECT_ID}/members?page=2&page_size=10"
        )

        assert response.status_code == 200
        mock_service.list_members.assert_called_once_with(
            user_id=_OWNER_ID,
            project_id=_PROJECT_ID,
            page=2,
            page_size=10,
        )


# ---------------------------------------------------------------------------
# Add Member -- POST /api/v1/projects/{project_id}/members
# ---------------------------------------------------------------------------


class TestAddMember:
    """POST /projects/{id}/members -- add a project member."""

    @pytest.mark.asyncio
    async def test_success(self, client, mock_service, mock_current_user) -> None:
        """Returns 201 with the new member."""
        member = _make_member_response(user_id=_OTHER_ID)
        mock_service.add_member.return_value = member

        response = await client.post(
            f"/api/v1/projects/{_PROJECT_ID}/members",
            json={"user_id": str(_OTHER_ID), "role": "MEMBER"},
        )

        assert response.status_code == 201
        assert response.json()["user_id"] == str(_OTHER_ID)

    @pytest.mark.asyncio
    async def test_already_exists(self, client, mock_service, mock_current_user) -> None:
        """A duplicate member yields 409."""
        from app.core.exceptions import MemberAlreadyExistsError

        mock_service.add_member.side_effect = MemberAlreadyExistsError()

        response = await client.post(
            f"/api/v1/projects/{_PROJECT_ID}/members",
            json={"user_id": str(_OTHER_ID)},
        )

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_insufficient_permission(
        self, client, mock_service, mock_current_user
    ) -> None:
        """Caller lacks permission yields 403."""
        mock_service.add_member.side_effect = InsufficientPermissionError()

        response = await client.post(
            f"/api/v1/projects/{_PROJECT_ID}/members",
            json={"user_id": str(_OTHER_ID)},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_not_found(self, client, mock_service, mock_current_user) -> None:
        """A non-existent project yields 404."""
        mock_service.add_member.side_effect = ProjectNotFoundError()

        response = await client.post(
            f"/api/v1/projects/{uuid4()}/members",
            json={"user_id": str(_OTHER_ID)},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_no_auth(self, client, mock_service, mock_no_auth) -> None:
        """Missing authentication yields a 401 error."""
        response = await client.post(
            f"/api/v1/projects/{_PROJECT_ID}/members",
            json={"user_id": str(_OTHER_ID)},
        )

        assert response.status_code == 401
# ---------------------------------------------------------------------------
# Update Member Role -- PATCH /api/v1/projects/{project_id}/members/{user_id}
# ---------------------------------------------------------------------------


class TestUpdateMemberRole:
    """PATCH /projects/{id}/members/{uid} -- update a member's role."""

    @pytest.mark.asyncio
    async def test_success(self, client, mock_service, mock_current_user) -> None:
        """Returns 200 with the updated member."""
        updated = _make_member_response(role=ProjectRole.ADMIN)
        mock_service.update_member_role.return_value = updated

        response = await client.patch(
            f"/api/v1/projects/{_PROJECT_ID}/members/{_OTHER_ID}",
            json={"role": "ADMIN"},
        )

        assert response.status_code == 200
        assert response.json()["role"] == "ADMIN"

    @pytest.mark.asyncio
    async def test_not_found(self, client, mock_service, mock_current_user) -> None:
        """A non-existent member yields 404."""
        mock_service.update_member_role.side_effect = MemberNotFoundError()

        response = await client.patch(
            f"/api/v1/projects/{_PROJECT_ID}/members/{uuid4()}",
            json={"role": "ADMIN"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_insufficient_permission(
        self, client, mock_service, mock_current_user
    ) -> None:
        """Caller lacks permission yields 403."""
        mock_service.update_member_role.side_effect = InsufficientPermissionError()

        response = await client.patch(
            f"/api/v1/projects/{_PROJECT_ID}/members/{_OTHER_ID}",
            json={"role": "ADMIN"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_no_auth(self, client, mock_service, mock_no_auth) -> None:
        """Missing authentication yields a 401 error."""
        response = await client.patch(
            f"/api/v1/projects/{_PROJECT_ID}/members/{_OTHER_ID}",
            json={"role": "ADMIN"},
        )

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Remove Member -- DELETE /api/v1/projects/{project_id}/members/{user_id}
# ---------------------------------------------------------------------------


class TestRemoveMember:
    """DELETE /projects/{id}/members/{uid} -- remove a project member."""

    @pytest.mark.asyncio
    async def test_success(self, client, mock_service, mock_current_user) -> None:
        """Returns 204 with no content."""
        mock_service.remove_member.return_value = None

        response = await client.delete(
            f"/api/v1/projects/{_PROJECT_ID}/members/{_OTHER_ID}"
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_not_found(self, client, mock_service, mock_current_user) -> None:
        """A non-existent member yields 404."""
        mock_service.remove_member.side_effect = MemberNotFoundError()

        response = await client.delete(
            f"/api/v1/projects/{_PROJECT_ID}/members/{uuid4()}"
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_insufficient_permission(
        self, client, mock_service, mock_current_user
    ) -> None:
        """Caller lacks permission yields 403."""
        mock_service.remove_member.side_effect = InsufficientPermissionError()

        response = await client.delete(
            f"/api/v1/projects/{_PROJECT_ID}/members/{_OTHER_ID}"
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_no_auth(self, client, mock_service, mock_no_auth) -> None:
        """Missing authentication yields a 401 error."""
        response = await client.delete(
            f"/api/v1/projects/{_PROJECT_ID}/members/{_OTHER_ID}"
        )

        assert response.status_code == 401