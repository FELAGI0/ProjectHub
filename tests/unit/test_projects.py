"""Unit tests for the ProjectService layer.

Mocks the ProjectRepository to test business logic and ownership enforcement
in isolation from the database.
"""

from datetime import UTC, datetime
from unittest import mock
from uuid import UUID, uuid4

import pytest

from app.core.exceptions import ProjectAccessDeniedError, ProjectNotFoundError
from app.modules.projects.models import Project
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schemas import ProjectCreateRequest, ProjectUpdateRequest
from app.modules.projects.service import ProjectService

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_OWNER_ID = uuid4()
_OTHER_ID = uuid4()
_PROJECT_ID = uuid4()


def _make_project(
    project_id: UUID | None = None,
    owner_id: UUID | None = None,
    name: str = "Test Project",
) -> Project:
    """Build a Project ORM instance for use as a mock return value."""
    return Project(
        id=project_id or _PROJECT_ID,
        owner_id=owner_id or _OWNER_ID,
        name=name,
        description="A description",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_repo():
    """A mock ProjectRepository with all async methods returning defaults."""
    repo = mock.AsyncMock(spec=ProjectRepository)
    repo.get_by_id.return_value = None
    repo.get_owned.return_value = ([], 0)
    repo.create.return_value = _make_project()
    repo.update.return_value = _make_project()
    return repo


@pytest.fixture
def service(mock_repo):
    """A ProjectService with a mocked repository and session."""
    session = mock.AsyncMock()
    settings = mock.MagicMock()
    svc = ProjectService(session, settings)
    svc._projects = mock_repo
    svc._session = session
    return svc


# ---------------------------------------------------------------------------
# list_projects
# ---------------------------------------------------------------------------


class TestListProjects:
    """list_projects delegates filtering/pagination to the repository."""

    @pytest.mark.asyncio
    async def test_empty(self, service, mock_repo) -> None:
        """When no projects exist, the response has an empty items list."""
        mock_repo.get_owned.return_value = ([], 0)

        result = await service.list_projects(owner_id=_OWNER_ID)

        assert result.items == []
        assert result.total == 0
        assert result.total_pages == 1

    @pytest.mark.asyncio
    async def test_paginated_result(self, service, mock_repo) -> None:
        """A single project is returned with correct pagination metadata."""
        project = _make_project()
        mock_repo.get_owned.return_value = ([project], 1)

        result = await service.list_projects(owner_id=_OWNER_ID, page=1, page_size=20)

        assert len(result.items) == 1
        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 20
        assert result.total_pages == 1

    @pytest.mark.asyncio
    async def test_passes_search_filter(self, service, mock_repo) -> None:
        """The search parameter is forwarded to the repository."""
        mock_repo.get_owned.return_value = ([], 0)

        await service.list_projects(
            owner_id=_OWNER_ID, search="search-term", is_active=True
        )

        mock_repo.get_owned.assert_called_once_with(
            owner_id=_OWNER_ID,
            page=1,
            page_size=20,
            search="search-term",
            is_active=True,
        )


# ---------------------------------------------------------------------------
# create_project
# ---------------------------------------------------------------------------


class TestCreateProject:
    """create_project creates a project and commits the transaction."""

    @pytest.mark.asyncio
    async def test_creates_and_commits(self, service, mock_repo) -> None:
        """A valid request creates a project and commits the session."""
        payload = ProjectCreateRequest(name="New Project", description="Desc")

        result = await service.create_project(_OWNER_ID, payload)

        mock_repo.create.assert_awaited_once_with(
            owner_id=_OWNER_ID, name="New Project", description="Desc"
        )
        service._session.commit.assert_awaited_once()
        assert result.name == "Test Project"


# ---------------------------------------------------------------------------
# get_project
# ---------------------------------------------------------------------------


class TestGetProject:
    """get_project enforces ownership before returning a project."""

    @pytest.mark.asyncio
    async def test_success(self, service, mock_repo) -> None:
        """The project is returned when the caller is the owner."""
        project = _make_project(owner_id=_OWNER_ID)
        mock_repo.get_by_id.return_value = project

        result = await service.get_project(_OWNER_ID, _PROJECT_ID)

        assert result.id == _PROJECT_ID
        assert result.name == "Test Project"

    @pytest.mark.asyncio
    async def test_not_found(self, service, mock_repo) -> None:
        """ProjectNotFoundError is raised when the project does not exist."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await service.get_project(_OWNER_ID, uuid4())

    @pytest.mark.asyncio
    async def test_access_denied(self, service, mock_repo) -> None:
        """ProjectAccessDeniedError is raised for a project owned by another user."""
        project = _make_project(owner_id=_OTHER_ID)
        mock_repo.get_by_id.return_value = project

        with pytest.raises(ProjectAccessDeniedError):
            await service.get_project(_OWNER_ID, _PROJECT_ID)


# ---------------------------------------------------------------------------
# update_project
# ---------------------------------------------------------------------------


class TestUpdateProject:
    """update_project modifies fields and commits when ownership is verified."""

    @pytest.mark.asyncio
    async def test_updates_fields(self, service, mock_repo) -> None:
        """Owned project fields are updated and committed."""
        project = _make_project(owner_id=_OWNER_ID)
        mock_repo.get_by_id.return_value = project
        payload = ProjectUpdateRequest(name="Updated", description=None, is_active=None)

        await service.update_project(_OWNER_ID, _PROJECT_ID, payload)

        mock_repo.update.assert_awaited_once_with(
            project, name="Updated", description=None, is_active=None
        )
        service._session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_not_found(self, service, mock_repo) -> None:
        """ProjectNotFoundError is raised when the project does not exist."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await service.update_project(_OWNER_ID, _PROJECT_ID, ProjectUpdateRequest())

    @pytest.mark.asyncio
    async def test_access_denied(self, service, mock_repo) -> None:
        """ProjectAccessDeniedError is raised for another user's project."""
        project = _make_project(owner_id=_OTHER_ID)
        mock_repo.get_by_id.return_value = project

        with pytest.raises(ProjectAccessDeniedError):
            await service.update_project(_OWNER_ID, _PROJECT_ID, ProjectUpdateRequest())


# ---------------------------------------------------------------------------
# delete_project
# ---------------------------------------------------------------------------


class TestDeleteProject:
    """delete_project removes a project when ownership is verified."""

    @pytest.mark.asyncio
    async def test_deletes_and_commits(self, service, mock_repo) -> None:
        """Owned project is deleted and the session is committed."""
        project = _make_project(owner_id=_OWNER_ID)
        mock_repo.get_by_id.return_value = project

        await service.delete_project(_OWNER_ID, _PROJECT_ID)

        mock_repo.delete.assert_awaited_once_with(project)
        service._session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_not_found(self, service, mock_repo) -> None:
        """ProjectNotFoundError is raised when the project does not exist."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await service.delete_project(_OWNER_ID, _PROJECT_ID)

    @pytest.mark.asyncio
    async def test_access_denied(self, service, mock_repo) -> None:
        """ProjectAccessDeniedError is raised for another user's project."""
        project = _make_project(owner_id=_OTHER_ID)
        mock_repo.get_by_id.return_value = project

        with pytest.raises(ProjectAccessDeniedError):
            await service.delete_project(_OWNER_ID, _PROJECT_ID)
