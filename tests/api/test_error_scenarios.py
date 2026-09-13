"""Edge case tests for error scenarios and authorization."""

from datetime import UTC, datetime
from unittest import mock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies.auth import get_current_user
from app.api.v1.projects import get_project_service
from app.core.exceptions import (
    ProjectAccessDeniedError,
    ProjectNotFoundError,
)
from app.factory import create_application
from app.modules.projects.schemas import ProjectResponse
from app.modules.users.models import User

_OWNER_ID = uuid4()
_OTHER_USER_ID = uuid4()
_PROJECT_ID = uuid4()
_NOW = datetime.now(UTC)


def _make_project_response(owner_id: uuid4 = _OWNER_ID) -> ProjectResponse:
    """Build a valid ProjectResponse."""
    return ProjectResponse(
        id=_PROJECT_ID,
        name="Test Project",
        description="A test project",
        owner_id=owner_id,
        is_active=True,
        created_at=_NOW,
        updated_at=_NOW,
    )


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
    """Override get_project_service with an AsyncMock."""
    svc = mock.AsyncMock()
    app.dependency_overrides[get_project_service] = lambda: svc
    yield svc
    app.dependency_overrides.clear()


@pytest.fixture
def mock_owner_user(app):
    """Mock the current user as the project owner."""
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
def mock_other_user(app):
    """Mock the current user as a different user (not owner)."""
    user = User(
        id=_OTHER_USER_ID,
        email="other@example.com",
        username="other",
        password_hash="hashed-placeholder",
        is_active=True,
        created_at=_NOW,
        updated_at=_NOW,
    )
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    app.dependency_overrides.clear()


class TestProjectErrorScenarios:
    """Test error scenarios and edge cases for project endpoints."""

    @pytest.mark.asyncio
    async def test_get_project_not_found(
        self, client, mock_service, mock_owner_user
    ) -> None:
        """Getting a non-existent project returns 404."""
        mock_service.get_project.side_effect = ProjectNotFoundError()

        response = await client.get(f"/api/v1/projects/{_PROJECT_ID}")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_get_project_access_denied(
        self, client, mock_service, mock_other_user
    ) -> None:
        """Non-owner cannot access project returns 403."""
        mock_service.get_project.side_effect = ProjectAccessDeniedError()

        response = await client.get(f"/api/v1/projects/{_PROJECT_ID}")

        assert response.status_code == 403
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_update_project_not_found(
        self, client, mock_service, mock_owner_user
    ) -> None:
        """Updating non-existent project returns 404."""
        mock_service.update_project.side_effect = ProjectNotFoundError()

        response = await client.patch(
            f"/api/v1/projects/{_PROJECT_ID}",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_project_access_denied(
        self, client, mock_service, mock_other_user
    ) -> None:
        """Non-owner cannot update project returns 403."""
        mock_service.update_project.side_effect = ProjectAccessDeniedError()

        response = await client.patch(
            f"/api/v1/projects/{_PROJECT_ID}",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_project_not_found(
        self, client, mock_service, mock_owner_user
    ) -> None:
        """Deleting non-existent project returns 404."""
        mock_service.delete_project.side_effect = ProjectNotFoundError()

        response = await client.delete(f"/api/v1/projects/{_PROJECT_ID}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_project_access_denied(
        self, client, mock_service, mock_other_user
    ) -> None:
        """Non-owner cannot delete project returns 403."""
        mock_service.delete_project.side_effect = ProjectAccessDeniedError()

        response = await client.delete(f"/api/v1/projects/{_PROJECT_ID}")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_project_empty_name(
        self, client, mock_service, mock_owner_user
    ) -> None:
        """Creating project with empty name returns 422."""
        response = await client.post(
            "/api/v1/projects/",
            json={"name": "", "description": "desc"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_project_name_too_long(
        self, client, mock_service, mock_owner_user
    ) -> None:
        """Creating project with very long name returns 422."""
        long_name = "x" * 300
        response = await client.post(
            "/api/v1/projects/",
            json={"name": long_name},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_projects_pagination_invalid_page(
        self, client, mock_service, mock_owner_user
    ) -> None:
        """Invalid page parameter returns 422."""
        response = await client.get("/api/v1/projects/?page=0&page_size=20")

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_projects_pagination_invalid_page_size(
        self, client, mock_service, mock_owner_user
    ) -> None:
        """Invalid page_size parameter returns 422."""
        response = await client.get("/api/v1/projects/?page=1&page_size=0")

        assert response.status_code == 422
