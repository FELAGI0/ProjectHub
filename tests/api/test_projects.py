"""Tests for the project management API endpoints.

Endpoints under test:
  GET    /api/v1/projects/
  POST   /api/v1/projects/
  GET    /api/v1/projects/{project_id}
  PATCH  /api/v1/projects/{project_id}
  DELETE /api/v1/projects/{project_id}

Dependencies are mocked via `app.dependency_overrides` so no database is required.
"""

from datetime import UTC, datetime
from unittest import mock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies.auth import get_current_user
from app.api.v1.projects import get_project_service
from app.core.exceptions import ProjectAccessDeniedError, ProjectNotFoundError
from app.factory import create_application
from app.modules.projects.schemas import (
    PaginatedProjectsResponse,
    ProjectResponse,
)
from app.modules.users.models import User

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_OWNER_ID = uuid4()
_PROJECT_ID = uuid4()
_NOW = datetime.now(UTC)


def _make_project_response() -> ProjectResponse:
    """Build a valid ProjectResponse for use as a mock return value."""
    return ProjectResponse(
        id=_PROJECT_ID,
        name="Test Project",
        description="A test project",
        owner_id=_OWNER_ID,
        is_active=True,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _paginated_response(
    items: list[ProjectResponse] | None = None,
) -> PaginatedProjectsResponse:
    """Build a paginated response for use as a mock return value."""
    items = items or [_make_project_response()]
    return PaginatedProjectsResponse(
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
    """Override get_project_service with an AsyncMock and yield the mock."""
    svc = mock.AsyncMock()
    app.dependency_overrides[get_project_service] = lambda: svc
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
    )  # noqa: E501
    yield
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Create -- POST /api/v1/projects/
# ---------------------------------------------------------------------------


class TestCreateProject:
    """POST /projects/ -- create a new project."""

    @pytest.mark.asyncio
    async def test_success(self, client, mock_service, mock_current_user) -> None:
        """A valid payload returns 201 with the project."""
        mock_service.create_project.return_value = _make_project_response()

        response = await client.post(
            "/api/v1/projects/",
            json={"name": "My Project", "description": "A description"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["owner_id"] == str(_OWNER_ID)

    @pytest.mark.asyncio
    async def test_validation_error(
        self, client, mock_service, mock_current_user
    ) -> None:  # noqa: E501
        """An empty name yields a 422 validation error."""
        response = await client.post(
            "/api/v1/projects/",
            json={"name": "", "description": "desc"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_no_auth(self, client, mock_service, mock_no_auth) -> None:
        """Missing authentication yields a 401 error."""
        response = await client.post(
            "/api/v1/projects/",
            json={"name": "My Project", "description": "desc"},
        )

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# List -- GET /api/v1/projects/
# ---------------------------------------------------------------------------


class TestListProjects:
    """GET /projects/ -- list projects owned by the authenticated user."""

    @pytest.mark.asyncio
    async def test_success(self, client, mock_service, mock_current_user) -> None:
        """Returns 200 with paginated results."""
        mock_service.list_projects.return_value = _paginated_response()

        response = await client.get("/api/v1/projects/")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["page_size"] == 20

    @pytest.mark.asyncio
    async def test_with_filters(self, client, mock_service, mock_current_user) -> None:
        """Query parameters are forwarded to the service."""
        mock_service.list_projects.return_value = _paginated_response(items=[])

        response = await client.get(
            "/api/v1/projects/?page=2&page_size=10&search=test&is_active=true"
        )

        assert response.status_code == 200
        mock_service.list_projects.assert_called_once_with(
            owner_id=_OWNER_ID, page=2, page_size=10, search="test", is_active=True
        )

    @pytest.mark.asyncio
    async def test_no_auth(self, client, mock_service, mock_no_auth) -> None:
        """Missing authentication yields a 401 error."""
        response = await client.get("/api/v1/projects/")

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Get -- GET /api/v1/projects/{project_id}
# ---------------------------------------------------------------------------


class TestGetProject:
    """GET /projects/{id} -- get a single project."""

    @pytest.mark.asyncio
    async def test_success(self, client, mock_service, mock_current_user) -> None:
        """Returns 200 with the project."""
        mock_service.get_project.return_value = _make_project_response()

        response = await client.get(f"/api/v1/projects/{_PROJECT_ID}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(_PROJECT_ID)

    @pytest.mark.asyncio
    async def test_not_found(self, client, mock_service, mock_current_user) -> None:
        """A non-existent project yields 404."""
        mock_service.get_project.side_effect = ProjectNotFoundError()

        response = await client.get(f"/api/v1/projects/{uuid4()}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Project was not found."}

    @pytest.mark.asyncio
    async def test_access_denied(self, client, mock_service, mock_current_user) -> None:
        """A project owned by another user yields 403."""
        mock_service.get_project.side_effect = ProjectAccessDeniedError()

        response = await client.get(f"/api/v1/projects/{uuid4()}")

        assert response.status_code == 403
        assert response.json() == {"detail": "You do not have access to this project."}

    @pytest.mark.asyncio
    async def test_no_auth(self, client, mock_service, mock_no_auth) -> None:
        """Missing authentication yields a 401 error."""
        response = await client.get(f"/api/v1/projects/{_PROJECT_ID}")

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Update -- PATCH /api/v1/projects/{project_id}
# ---------------------------------------------------------------------------


class TestUpdateProject:
    """PATCH /projects/{id} -- partially update a project."""

    @pytest.mark.asyncio
    async def test_success(self, client, mock_service, mock_current_user) -> None:
        """Returns 200 with the updated project."""
        updated = _make_project_response()
        updated.name = "Updated Name"
        mock_service.update_project.return_value = updated

        response = await client.patch(
            f"/api/v1/projects/{_PROJECT_ID}",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_not_found(self, client, mock_service, mock_current_user) -> None:
        """A non-existent project yields 404."""
        mock_service.update_project.side_effect = ProjectNotFoundError()

        response = await client.patch(
            f"/api/v1/projects/{uuid4()}",
            json={"name": "New Name"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_access_denied(self, client, mock_service, mock_current_user) -> None:
        """Another user's project yields 403."""
        mock_service.update_project.side_effect = ProjectAccessDeniedError()

        response = await client.patch(
            f"/api/v1/projects/{uuid4()}",
            json={"name": "New Name"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_no_auth(self, client, mock_service, mock_no_auth) -> None:
        """Missing authentication yields a 401 error."""
        response = await client.patch(
            f"/api/v1/projects/{_PROJECT_ID}",
            json={"name": "New Name"},
        )

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Delete -- DELETE /api/v1/projects/{project_id}
# ---------------------------------------------------------------------------


class TestDeleteProject:
    """DELETE /projects/{id} -- permanently delete a project."""

    @pytest.mark.asyncio
    async def test_success(self, client, mock_service, mock_current_user) -> None:
        """Returns 204 with no content."""
        mock_service.delete_project.return_value = None

        response = await client.delete(f"/api/v1/projects/{_PROJECT_ID}")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_not_found(self, client, mock_service, mock_current_user) -> None:
        """A non-existent project yields 404."""
        mock_service.delete_project.side_effect = ProjectNotFoundError()

        response = await client.delete(f"/api/v1/projects/{uuid4()}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Project was not found."}

    @pytest.mark.asyncio
    async def test_access_denied(self, client, mock_service, mock_current_user) -> None:
        """Another user's project yields 403."""
        mock_service.delete_project.side_effect = ProjectAccessDeniedError()

        response = await client.delete(f"/api/v1/projects/{uuid4()}")

        assert response.status_code == 403
        assert response.json() == {"detail": "You do not have access to this project."}

    @pytest.mark.asyncio
    async def test_no_auth(self, client, mock_service, mock_no_auth) -> None:
        """Missing authentication yields a 401 error."""
        response = await client.delete(f"/api/v1/projects/{_PROJECT_ID}")

        assert response.status_code == 401
