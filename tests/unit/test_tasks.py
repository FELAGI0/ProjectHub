"""Unit tests for the TaskService layer.

Mocks TaskRepository, ProjectRepository and ProjectMemberRepository to test
business logic and membership-based authorization in isolation.
"""

from datetime import UTC, datetime
from unittest import mock
from uuid import UUID, uuid4

import pytest

from app.core.exceptions import (
    ProjectNotFoundError,
    TaskNotFoundError,
)
from app.modules.project_members.models import ProjectMember, ProjectRole
from app.modules.projects.models import Project
from app.modules.tasks.models import Task, TaskPriority, TaskStatus
from app.modules.tasks.repository import TaskRepository
from app.modules.tasks.schemas import TaskCreateRequest, TaskUpdateRequest
from app.modules.tasks.service import TaskService

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_OWNER_ID = uuid4()
_OTHER_ID = uuid4()
_PROJECT_ID = uuid4()
_TASK_ID = uuid4()


def _make_project() -> Project:
    """Build a Project ORM instance for use as a mock return value."""
    return Project(
        id=_PROJECT_ID,
        name="Test Project",
        description="A description",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _make_member(
    role: ProjectRole = ProjectRole.OWNER,
) -> ProjectMember:
    """Build a ProjectMember ORM instance for use as a mock return value."""
    return ProjectMember(
        project_id=_PROJECT_ID,
        user_id=_OWNER_ID,
        role=role,
    )


def _make_task(task_id: UUID | None = None) -> Task:
    """Build a Task ORM instance for use as a mock return value."""
    return Task(
        id=task_id or _TASK_ID,
        project_id=_PROJECT_ID,
        title="Test Task",
        description="A task description",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_task_repo():
    """A mock TaskRepository with all async methods returning defaults."""
    repo = mock.AsyncMock(spec=TaskRepository)
    repo.get_by_id.return_value = None
    repo.get_project_tasks.return_value = ([], 0)
    repo.create.return_value = _make_task()
    repo.update.return_value = _make_task()
    return repo


@pytest.fixture
def mock_project_repo():
    """A mock ProjectRepository for project existence lookups."""
    repo = mock.AsyncMock()
    repo.get_by_id.return_value = None
    return repo


@pytest.fixture
def mock_member_repo():
    """A mock ProjectMemberRepository for membership checks."""
    repo = mock.AsyncMock()
    repo.get_by_project_and_user.return_value = None
    return repo


@pytest.fixture
def service(mock_task_repo, mock_project_repo, mock_member_repo):
    """A TaskService with mocked repositories and session."""
    session = mock.AsyncMock()
    settings = mock.MagicMock()
    svc = TaskService(session, settings)
    svc._tasks = mock_task_repo
    svc._projects = mock_project_repo
    svc._members = mock_member_repo
    svc._session = session
    return svc


# ---------------------------------------------------------------------------
# list_tasks
# ---------------------------------------------------------------------------


class TestListTasks:
    """list_tasks verifies project membership then delegates to the repository."""

    @pytest.mark.asyncio
    async def test_empty(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """When no tasks exist, the response has an empty items list."""
        mock_project_repo.get_by_id.return_value = _make_project()
        mock_member_repo.get_by_project_and_user.return_value = _make_member()
        mock_task_repo.get_project_tasks.return_value = ([], 0)

        result = await service.list_tasks(user_id=_OWNER_ID, project_id=_PROJECT_ID)

        assert result.items == []
        assert result.total == 0
        assert result.total_pages == 1

    @pytest.mark.asyncio
    async def test_paginated_result(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """A single task is returned with correct pagination metadata."""
        mock_project_repo.get_by_id.return_value = _make_project()
        mock_member_repo.get_by_project_and_user.return_value = _make_member()
        task = _make_task()
        mock_task_repo.get_project_tasks.return_value = ([task], 1)

        result = await service.list_tasks(
            user_id=_OWNER_ID, project_id=_PROJECT_ID, page=1, page_size=20
        )

        assert len(result.items) == 1
        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 20
        assert result.total_pages == 1

    @pytest.mark.asyncio
    async def test_forwards_filters(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """Filters (status, priority, search) are forwarded to the repository."""
        mock_project_repo.get_by_id.return_value = _make_project()
        mock_member_repo.get_by_project_and_user.return_value = _make_member()

        await service.list_tasks(
            user_id=_OWNER_ID,
            project_id=_PROJECT_ID,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            search="urgent",
        )

        mock_task_repo.get_project_tasks.assert_awaited_once_with(
            project_id=_PROJECT_ID,
            page=1,
            page_size=20,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            search="urgent",
        )

    @pytest.mark.asyncio
    async def test_project_not_found(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """ProjectNotFoundError is raised when the project does not exist."""
        mock_project_repo.get_by_id.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await service.list_tasks(user_id=_OWNER_ID, project_id=_PROJECT_ID)

        mock_task_repo.get_project_tasks.assert_not_called()

    @pytest.mark.asyncio
    async def test_project_access_denied(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """ProjectNotFoundError is raised for a non-member."""
        mock_project_repo.get_by_id.return_value = _make_project()
        mock_member_repo.get_by_project_and_user.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await service.list_tasks(user_id=_OWNER_ID, project_id=_PROJECT_ID)

        mock_task_repo.get_project_tasks.assert_not_called()


# ---------------------------------------------------------------------------
# create_task
# ---------------------------------------------------------------------------


class TestCreateTask:
    """create_task verifies project membership, creates, and commits."""

    @pytest.mark.asyncio
    async def test_creates_and_commits(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """A valid request creates a task and commits the session."""
        mock_project_repo.get_by_id.return_value = _make_project()
        mock_member_repo.get_by_project_and_user.return_value = _make_member()
        payload = TaskCreateRequest(
            title="New Task",
            description="Details",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            due_date=datetime.now(UTC),
        )

        result = await service.create_task(_OWNER_ID, _PROJECT_ID, payload)

        mock_task_repo.create.assert_awaited_once()
        service._session.commit.assert_awaited_once()
        assert result.title == "Test Task"

    @pytest.mark.asyncio
    async def test_project_not_found(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """ProjectNotFoundError is raised when the project does not exist."""
        mock_project_repo.get_by_id.return_value = None
        payload = TaskCreateRequest(title="New Task")

        with pytest.raises(ProjectNotFoundError):
            await service.create_task(_OWNER_ID, _PROJECT_ID, payload)

        mock_task_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_project_access_denied(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """ProjectNotFoundError is raised for a non-member."""
        mock_project_repo.get_by_id.return_value = _make_project()
        mock_member_repo.get_by_project_and_user.return_value = None
        payload = TaskCreateRequest(title="New Task")

        with pytest.raises(ProjectNotFoundError):
            await service.create_task(_OWNER_ID, _PROJECT_ID, payload)

        mock_task_repo.create.assert_not_called()


# ---------------------------------------------------------------------------
# get_task
# ---------------------------------------------------------------------------


class TestGetTask:
    """get_task returns the task when the user is a member of the parent project."""

    @pytest.mark.asyncio
    async def test_success(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """Task is returned as a validated response."""
        task = _make_task()
        mock_task_repo.get_by_id.return_value = task
        mock_project_repo.get_by_id.return_value = _make_project()
        mock_member_repo.get_by_project_and_user.return_value = _make_member()

        result = await service.get_task(_OWNER_ID, _TASK_ID)

        assert result.id == _TASK_ID
        assert result.title == "Test Task"

    @pytest.mark.asyncio
    async def test_not_found(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """TaskNotFoundError is raised when the task does not exist."""
        mock_task_repo.get_by_id.return_value = None

        with pytest.raises(TaskNotFoundError):
            await service.get_task(_OWNER_ID, _TASK_ID)

    @pytest.mark.asyncio
    async def test_project_not_found(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """ProjectNotFoundError is raised when the parent project is gone."""
        task = _make_task()
        mock_task_repo.get_by_id.return_value = task
        mock_project_repo.get_by_id.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await service.get_task(_OWNER_ID, _TASK_ID)

    @pytest.mark.asyncio
    async def test_access_denied(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """ProjectNotFoundError is raised for a non-member."""
        task = _make_task()
        mock_task_repo.get_by_id.return_value = task
        mock_project_repo.get_by_id.return_value = _make_project()
        mock_member_repo.get_by_project_and_user.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await service.get_task(_OWNER_ID, _TASK_ID)


# ---------------------------------------------------------------------------
# update_task
# ---------------------------------------------------------------------------


class TestUpdateTask:
    """update_task modifies fields and commits when membership is verified."""

    @pytest.mark.asyncio
    async def test_updates_fields(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """Task fields are updated and committed."""
        task = _make_task()
        mock_task_repo.get_by_id.return_value = task
        mock_project_repo.get_by_id.return_value = _make_project()
        mock_member_repo.get_by_project_and_user.return_value = _make_member()
        payload = TaskUpdateRequest(title="Updated", status=TaskStatus.DONE)

        await service.update_task(_OWNER_ID, _TASK_ID, payload)

        mock_task_repo.update.assert_awaited_once_with(
            task,
            title="Updated",
            description=None,
            status=TaskStatus.DONE,
            priority=None,
            due_date=None,
        )
        service._session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_not_found(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """TaskNotFoundError is raised when the task does not exist."""
        mock_task_repo.get_by_id.return_value = None

        with pytest.raises(TaskNotFoundError):
            await service.update_task(_OWNER_ID, _TASK_ID, TaskUpdateRequest())

    @pytest.mark.asyncio
    async def test_access_denied(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """ProjectNotFoundError is raised for a non-member."""
        task = _make_task()
        mock_task_repo.get_by_id.return_value = task
        mock_project_repo.get_by_id.return_value = _make_project()
        mock_member_repo.get_by_project_and_user.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await service.update_task(_OWNER_ID, _TASK_ID, TaskUpdateRequest())


# ---------------------------------------------------------------------------
# delete_task
# ---------------------------------------------------------------------------


class TestDeleteTask:
    """delete_task removes a task when membership is verified."""

    @pytest.mark.asyncio
    async def test_deletes_and_commits(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """Task is deleted and the session is committed."""
        task = _make_task()
        mock_task_repo.get_by_id.return_value = task
        mock_project_repo.get_by_id.return_value = _make_project()
        mock_member_repo.get_by_project_and_user.return_value = _make_member()

        await service.delete_task(_OWNER_ID, _TASK_ID)

        mock_task_repo.delete.assert_awaited_once_with(task)
        service._session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_not_found(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """TaskNotFoundError is raised when the task does not exist."""
        mock_task_repo.get_by_id.return_value = None

        with pytest.raises(TaskNotFoundError):
            await service.delete_task(_OWNER_ID, _TASK_ID)

    @pytest.mark.asyncio
    async def test_access_denied(
        self, service, mock_project_repo, mock_member_repo, mock_task_repo
    ) -> None:
        """ProjectNotFoundError is raised for a non-member."""
        task = _make_task()
        mock_task_repo.get_by_id.return_value = task
        mock_project_repo.get_by_id.return_value = _make_project()
        mock_member_repo.get_by_project_and_user.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await service.delete_task(_OWNER_ID, _TASK_ID)
