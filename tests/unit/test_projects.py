"""Unit tests for the ProjectService layer.

Mocks the ProjectRepository and ProjectMemberRepository to test business logic
and membership-based authorization in isolation from the database.
"""

from datetime import UTC, datetime
from unittest import mock
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    ConflictError,
    DomainError,
    InsufficientPermissionError,
    ProjectAccessDeniedError,
    ProjectNotFoundError,
)
from app.modules.project_members.models import ProjectMember, ProjectRole
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.projects.models import Project
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schemas import ProjectCreateRequest, ProjectUpdateRequest
from app.modules.projects.service import ProjectService

# Import all models to ensure SQLAlchemy registry is configured
from app.modules.tasks.models import Task  # noqa: F401
from app.modules.users.models import User  # noqa: F401

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_OWNER_ID = uuid4()
_OTHER_ID = uuid4()
_PROJECT_ID = uuid4()
_USER_B_ID = uuid4()


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


def _make_member(
    user_id: UUID | None = None,
    role: ProjectRole = ProjectRole.OWNER,
) -> ProjectMember:
    """Build a ProjectMember ORM instance for use as a mock return value."""
    return ProjectMember(
        id=uuid4(),
        project_id=_PROJECT_ID,
        user_id=user_id or _OWNER_ID,
        role=role,
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
    repo.get_member_projects.return_value = ([], 0)
    repo.create.return_value = _make_project()
    repo.update.return_value = _make_project()
    return repo


@pytest.fixture
def mock_member_repo():
    """A mock ProjectMemberRepository for membership checks."""
    repo = mock.AsyncMock(spec=ProjectMemberRepository)
    repo.get_by_project_and_user.return_value = None
    repo.create.return_value = _make_member()
    return repo


@pytest.fixture
def service(mock_repo, mock_member_repo):
    """A ProjectService with mocked repositories and session."""
    session = mock.AsyncMock()
    settings = mock.MagicMock()
    svc = ProjectService(session, settings)
    svc._projects = mock_repo
    svc._members = mock_member_repo
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
        mock_repo.get_member_projects.return_value = ([], 0)

        result = await service.list_projects(user_id=_OWNER_ID)

        assert result.items == []
        assert result.total == 0
        assert result.total_pages == 1

    @pytest.mark.asyncio
    async def test_paginated_result(self, service, mock_repo) -> None:
        """A single project is returned with correct pagination metadata."""
        project = _make_project()
        mock_repo.get_member_projects.return_value = ([project], 1)

        result = await service.list_projects(user_id=_OWNER_ID, page=1, page_size=20)

        assert len(result.items) == 1
        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 20
        assert result.total_pages == 1

    @pytest.mark.asyncio
    async def test_search_pass_through(self, service, mock_repo) -> None:
        """Search term and active flag are forwarded to the repository."""
        await service.list_projects(
            user_id=_OWNER_ID,
            page=2,
            page_size=10,
            search="keyword",
            is_active=True,
        )

        mock_repo.get_member_projects.assert_awaited_once_with(
            user_id=_OWNER_ID,
            page=2,
            page_size=10,
            search="keyword",
            is_active=True,
        )


# ---------------------------------------------------------------------------
# create_project
# ---------------------------------------------------------------------------


class TestCreateProject:
    """create_project creates a project and an OWNER membership."""

    @pytest.mark.asyncio
    async def test_creates_project_and_membership(
        self, service, mock_repo, mock_member_repo
    ) -> None:
        """Project and OWNER member are created, and the session is committed."""
        payload = ProjectCreateRequest(name="New Project")

        result = await service.create_project(_OWNER_ID, payload)

        mock_repo.create.assert_awaited_once_with(
            owner_id=_OWNER_ID, name="New Project", description=None
        )
        mock_member_repo.create.assert_awaited_once_with(
            project_id=_PROJECT_ID,
            user_id=_OWNER_ID,
            role=ProjectRole.OWNER,
        )
        service._session.commit.assert_awaited_once()
        assert result.name == "Test Project"


# ---------------------------------------------------------------------------
# get_project
# ---------------------------------------------------------------------------


class TestGetProject:
    """get_project returns a project when the user is a member."""

    @pytest.mark.asyncio
    async def test_returns_project(self, service, mock_repo, mock_member_repo) -> None:
        """Returns the project when user is a member."""
        project = _make_project()
        mock_repo.get_by_id.return_value = project
        mock_member_repo.get_by_project_and_user.return_value = _make_member()

        result = await service.get_project(_OWNER_ID, _PROJECT_ID)

        assert result.id == _PROJECT_ID
        assert result.name == "Test Project"

    @pytest.mark.asyncio
    async def test_not_found(self, service, mock_repo, mock_member_repo) -> None:
        """ProjectNotFoundError is raised when the project does not exist."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await service.get_project(_OWNER_ID, _PROJECT_ID)

    @pytest.mark.asyncio
    async def test_access_denied(self, service, mock_repo, mock_member_repo) -> None:
        """ProjectAccessDeniedError is raised for a non-member."""
        project = _make_project()
        mock_repo.get_by_id.return_value = project
        mock_member_repo.get_by_project_and_user.return_value = None

        with pytest.raises(ProjectAccessDeniedError):
            await service.get_project(_OTHER_ID, _PROJECT_ID)


# ---------------------------------------------------------------------------
# update_project
# ---------------------------------------------------------------------------


class TestUpdateProject:
    """update_project modifies fields and commits when membership is verified."""

    @pytest.mark.asyncio
    async def test_updates_fields(self, service, mock_repo, mock_member_repo) -> None:
        """Project with ADMIN role is updated and committed."""
        project = _make_project()
        mock_repo.get_by_id.return_value = project
        mock_member_repo.get_by_project_and_user.return_value = _make_member(
            role=ProjectRole.ADMIN
        )
        payload = ProjectUpdateRequest(name="Updated", description=None, is_active=None)

        await service.update_project(_OWNER_ID, _PROJECT_ID, payload)

        mock_repo.update.assert_awaited_once_with(
            project, name="Updated", description=None, is_active=None
        )
        service._session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_not_found(self, service, mock_repo, mock_member_repo) -> None:
        """ProjectNotFoundError is raised when the project does not exist."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await service.update_project(_OWNER_ID, _PROJECT_ID, ProjectUpdateRequest())

    @pytest.mark.asyncio
    async def test_access_denied(self, service, mock_repo, mock_member_repo) -> None:
        """ProjectAccessDeniedError is raised for a non-member."""
        project = _make_project()
        mock_repo.get_by_id.return_value = project
        mock_member_repo.get_by_project_and_user.return_value = None

        with pytest.raises(ProjectAccessDeniedError):
            await service.update_project(_OWNER_ID, _PROJECT_ID, ProjectUpdateRequest())

    @pytest.mark.asyncio
    async def test_insufficient_permission(
        self, service, mock_repo, mock_member_repo
    ) -> None:
        """InsufficientPermissionError is raised for a MEMBER trying to update."""
        project = _make_project()
        mock_repo.get_by_id.return_value = project
        mock_member_repo.get_by_project_and_user.return_value = _make_member(
            role=ProjectRole.MEMBER
        )

        with pytest.raises(InsufficientPermissionError):
            await service.update_project(_OWNER_ID, _PROJECT_ID, ProjectUpdateRequest())


# ---------------------------------------------------------------------------
# delete_project
# ---------------------------------------------------------------------------


class TestDeleteProject:
    """delete_project removes a project when OWNER role is verified."""

    @pytest.mark.asyncio
    async def test_deletes_and_commits(
        self, service, mock_repo, mock_member_repo
    ) -> None:
        """Owned project is deleted and the session is committed."""
        project = _make_project()
        mock_repo.get_by_id.return_value = project
        mock_member_repo.get_by_project_and_user.return_value = _make_member(
            role=ProjectRole.OWNER
        )

        await service.delete_project(_OWNER_ID, _PROJECT_ID)

        mock_repo.delete.assert_awaited_once_with(project)
        service._session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_not_found(self, service, mock_repo, mock_member_repo) -> None:
        """ProjectNotFoundError is raised when the project does not exist."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await service.delete_project(_OWNER_ID, _PROJECT_ID)

    @pytest.mark.asyncio
    async def test_access_denied(self, service, mock_repo, mock_member_repo) -> None:
        """ProjectAccessDeniedError is raised for a non-member."""
        project = _make_project()
        mock_repo.get_by_id.return_value = project
        mock_member_repo.get_by_project_and_user.return_value = None

        with pytest.raises(ProjectAccessDeniedError):
            await service.delete_project(_OWNER_ID, _PROJECT_ID)

    @pytest.mark.asyncio
    async def test_insufficient_permission(
        self, service, mock_repo, mock_member_repo
    ) -> None:
        """InsufficientPermissionError is raised for a non-OWNER."""
        project = _make_project()
        mock_repo.get_by_id.return_value = project
        mock_member_repo.get_by_project_and_user.return_value = _make_member(
            role=ProjectRole.ADMIN
        )

        with pytest.raises(InsufficientPermissionError):
            await service.delete_project(_OWNER_ID, _PROJECT_ID)


# ---------------------------------------------------------------------------
# transfer_ownership
# ---------------------------------------------------------------------------


class TestTransferOwnership:
    """transfer_ownership changes roles and owner_id when authorized."""

    @pytest.mark.asyncio
    async def test_transfer_ownership_success(self, service, mock_member_repo) -> None:
        """Roles change, project.owner_id updated, session committed."""
        project = _make_project(owner_id=_OWNER_ID)
        caller_member = _make_member(user_id=_OWNER_ID, role=ProjectRole.OWNER)
        new_owner_member = _make_member(user_id=_USER_B_ID, role=ProjectRole.MEMBER)
        mock_member_repo.get_by_project_and_user.return_value = new_owner_member

        with patch(
            "app.modules.projects.service.require_project_membership",
            new=AsyncMock(return_value=(project, caller_member)),
        ):
            await service.transfer_ownership(_OWNER_ID, _PROJECT_ID, _USER_B_ID)

        assert caller_member.role == ProjectRole.ADMIN
        assert new_owner_member.role == ProjectRole.OWNER
        assert project.owner_id == _USER_B_ID
        service._session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_transfer_to_self_raises(self, service) -> None:
        """DomainError raised when transferring to self."""
        project = _make_project(owner_id=_OWNER_ID)
        caller_member = _make_member(user_id=_OWNER_ID, role=ProjectRole.OWNER)

        with (
            patch(
                "app.modules.projects.service.require_project_membership",
                new=AsyncMock(return_value=(project, caller_member)),
            ),
            pytest.raises(DomainError, match="Cannot transfer ownership to yourself"),
        ):
            await service.transfer_ownership(_OWNER_ID, _PROJECT_ID, _OWNER_ID)

        service._session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_transfer_to_non_member_raises(
        self, service, mock_member_repo
    ) -> None:
        """DomainError raised when new owner is not a member."""
        project = _make_project(owner_id=_OWNER_ID)
        caller_member = _make_member(user_id=_OWNER_ID, role=ProjectRole.OWNER)
        mock_member_repo.get_by_project_and_user.return_value = None

        with (
            patch(
                "app.modules.projects.service.require_project_membership",
                new=AsyncMock(return_value=(project, caller_member)),
            ),
            pytest.raises(DomainError, match="User is not a project member"),
        ):
            await service.transfer_ownership(_OWNER_ID, _PROJECT_ID, _USER_B_ID)

        service._session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_concurrent_transfer_raises_conflict(
        self, service, mock_member_repo
    ) -> None:
        """ConflictError raised on concurrent IntegrityError, session rolled back."""
        project = _make_project(owner_id=_OWNER_ID)
        caller_member = _make_member(user_id=_OWNER_ID, role=ProjectRole.OWNER)
        new_owner_member = _make_member(user_id=_USER_B_ID, role=ProjectRole.MEMBER)
        mock_member_repo.get_by_project_and_user.return_value = new_owner_member
        service._session.commit.side_effect = IntegrityError(
            "INSERT INTO project_members ...",
            {},
            Exception("duplicate key value violates unique constraint"),
        )

        with (
            patch(
                "app.modules.projects.service.require_project_membership",
                new=AsyncMock(return_value=(project, caller_member)),
            ),
            pytest.raises(ConflictError, match="Ownership was changed concurrently"),
        ):
            await service.transfer_ownership(_OWNER_ID, _PROJECT_ID, _USER_B_ID)

        service._session.rollback.assert_awaited_once()
