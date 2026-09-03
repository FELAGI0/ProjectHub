"""Tests for the task management API endpoints.

Endpoints under test:
  GET    /api/v1/projects/{project_id}/tasks
  POST   /api/v1/projects/{project_id}/tasks
  GET    /api/v1/tasks/{task_id}
  PUT    /api/v1/tasks/{task_id}
  DELETE /api/v1/tasks/{task_id}

Dependencies are mocked via `app.dependency_overrides` so no database is required.
"""

from datetime import UTC, datetime
from unittest import mock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies.auth import get_current_user
from app.api.v1.tasks import get_task_service
from app.core.exceptions import (
    ProjectAccessDeniedError,
    TaskNotFoundError,
)
from app.factory import create_application
from app.modules.tasks.models import TaskPriority, TaskStatus
from app.modules.tasks.schemas import (
    PaginatedTasksResponse,
    TaskResponse,
)
from app.modules.users.models import User

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_OWNER_ID = uuid4()
_PROJECT_ID = uuid4()
_TASK_ID = uuid4()
_NOW = datetime.now(UTC)


def _make_task_response() -> TaskResponse:
    """Build a valid TaskResponse for use as a mock return value."""
    return TaskResponse(
        id=_TASK_ID,
        project_id=_PROJECT_ID,
        title="Test Task",
        description="A task description",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        due_date=None,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _paginated_response(
    items: list[TaskResponse] | None = None,
) -> PaginatedTasksResponse:
    """Build a paginated response for use as a mock return value."""
    items = items or [_make_task_response()]
    return PaginatedTasksResponse(
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
    """Override get_task_service with an AsyncMock and yield the mock."""
    svc = mock.AsyncMock()
    app.dependency_overrides[get_task_service] = lambda: svc
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
# List -- GET /projects/{project_id}/tasks
# ---------------------------------------------------------------------------


class TestListTasks:
    """GET /projects/{id}/tasks -- paginated list of tasks."""

    @pytest.mark.asyncio
    async def test_success(self, client, mock_service, mock_current_user) -> None:
        """Returns 200 with a paginated task list."""
        mock_service.list_tasks.return_value = _paginated_response()

        response = await client.get(f"/api/v1/projects/{_PROJECT_ID}/tasks")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_with_filters(self, client, mock_service, mock_current_user) -> None:
        """Filters (status, priority, search) are accepted as query params."""
        mock_service.list_tasks.return_value = _paginated_response()

        response = await client.get(
            f"/api/v1/projects/{_PROJECT_ID}/tasks",
            params={
                "status": TaskStatus.IN_PROGRESS.value,
                "priority": TaskPriority.HIGH.value,
                "search": "urgent",
                "page": 1,
                "page_size": 10,
            },
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_no_auth(self, client, mock_service, mock_no_auth) -> None:
        """Missing authentication yields a 401 error."""
        response = await client.get(f"/api/v1/projects/{_PROJECT_ID}/tasks")

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Create -- POST /projects/{project_id}/tasks
# ---------------------------------------------------------------------------


class TestCreateTask:
    """POST /projects/{id}/tasks -- create a new task."""

    @pytest.mark.asyncio
    async def test_success(self, client, mock_service, mock_current_user) -> None:
        """Returns 201 with the created task."""
        mock_service.create_task.return_value = _make_task_response()

        response = await client.post(
            f"/api/v1/projects/{_PROJECT_ID}/tasks",
            json={"title": "New Task"},
        )

        assert response.status_code == 201
        assert response.json()["title"] == "Test Task"

    @pytest.mark.asyncio
    async def test_validation_error(
        self, client, mock_service, mock_current_user
    ) -> None:
        """An empty title yields a 422 validation error."""
        response = await client.post(
            f"/api/v1/projects/{_PROJECT_ID}/tasks",
            json={"title": ""},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_no_auth(self, client, mock_service, mock_no_auth) -> None:
        """Missing authentication yields a 401 error."""
        response = await client.post(
            f"/api/v1/projects/{_PROJECT_ID}/tasks",
            json={"title": "New Task"},
        )

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Get -- GET /tasks/{task_id}
# ---------------------------------------------------------------------------


class TestGetTask:
    """GET /tasks/{id} -- retrieve a single task."""

    @pytest.mark.asyncio
    async def test_success(self, client, mock_service, mock_current_user) -> None:
        """Returns 200 with the task payload."""
        mock_service.get_task.return_value = _make_task_response()

        response = await client.get(f"/api/v1/tasks/{_TASK_ID}")

        assert response.status_code == 200
        assert response.json()["id"] == str(_TASK_ID)

    @pytest.mark.asyncio
    async def test_not_found(self, client, mock_service, mock_current_user) -> None:
        """A non-existent task yields 404."""
        mock_service.get_task.side_effect = TaskNotFoundError()

        response = await client.get(f"/api/v1/tasks/{uuid4()}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Task was not found."}

    @pytest.mark.asyncio
    async def test_access_denied(self, client, mock_service, mock_current_user) -> None:
        """Another user's project yields 403."""
        mock_service.get_task.side_effect = ProjectAccessDeniedError()

        response = await client.get(f"/api/v1/tasks/{uuid4()}")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_no_auth(self, client, mock_service, mock_no_auth) -> None:
        """Missing authentication yields a 401 error."""
        response = await client.get(f"/api/v1/tasks/{_TASK_ID}")

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Update -- PUT /tasks/{task_id}
# ---------------------------------------------------------------------------


class TestUpdateTask:
    """PUT /tasks/{id} -- update a task."""

    @pytest.mark.asyncio
    async def test_success(self, client, mock_service, mock_current_user) -> None:
        """Returns 200 with the updated task."""
        updated = _make_task_response()
        updated.title = "Updated Title"
        mock_service.update_task.return_value = updated

        response = await client.put(
            f"/api/v1/tasks/{_TASK_ID}",
            json={"title": "Updated Title"},
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_not_found(self, client, mock_service, mock_current_user) -> None:
        """A non-existent task yields 404."""
        mock_service.update_task.side_effect = TaskNotFoundError()

        response = await client.put(
            f"/api/v1/tasks/{uuid4()}",
            json={"title": "New Title"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_access_denied(self, client, mock_service, mock_current_user) -> None:
        """Another user's project yields 403."""
        mock_service.update_task.side_effect = ProjectAccessDeniedError()

        response = await client.put(
            f"/api/v1/tasks/{uuid4()}",
            json={"title": "New Title"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_no_auth(self, client, mock_service, mock_no_auth) -> None:
        """Missing authentication yields a 401 error."""
        response = await client.put(
            f"/api/v1/tasks/{_TASK_ID}",
            json={"title": "New Title"},
        )

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Delete -- DELETE /tasks/{task_id}
# ---------------------------------------------------------------------------


class TestDeleteTask:
    """DELETE /tasks/{id} -- permanently delete a task."""

    @pytest.mark.asyncio
    async def test_success(self, client, mock_service, mock_current_user) -> None:
        """Returns 204 with no content."""
        mock_service.delete_task.return_value = None

        response = await client.delete(f"/api/v1/tasks/{_TASK_ID}")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_not_found(self, client, mock_service, mock_current_user) -> None:
        """A non-existent task yields 404."""
        mock_service.delete_task.side_effect = TaskNotFoundError()

        response = await client.delete(f"/api/v1/tasks/{uuid4()}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Task was not found."}

    @pytest.mark.asyncio
    async def test_access_denied(self, client, mock_service, mock_current_user) -> None:
        """Another user's project yields 403."""
        mock_service.delete_task.side_effect = ProjectAccessDeniedError()

        response = await client.delete(f"/api/v1/tasks/{uuid4()}")

        assert response.status_code == 403
        assert response.json() == {"detail": "You do not have access to this project."}

    @pytest.mark.asyncio
    async def test_no_auth(self, client, mock_service, mock_no_auth) -> None:
        """Missing authentication yields a 401 error."""
        response = await client.delete(f"/api/v1/tasks/{_TASK_ID}")

        assert response.status_code == 401
