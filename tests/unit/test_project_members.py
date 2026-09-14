"""Unit tests for the ProjectMemberService layer.

Mocks the ProjectMemberRepository and ProjectRepository to test business logic,
role-based authorization, and membership enforcement in isolation.
"""

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest import mock
from uuid import UUID, uuid4

import pytest

from app.core.exceptions import (
    InsufficientPermissionError,
    MemberNotFoundError,
    ProjectNotFoundError,
)
from app.modules.project_members.models import ProjectMember, ProjectRole
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.project_members.schemas import (
    MemberAddRequest,
    MemberRoleUpdateRequest,
)
from app.modules.project_members.service import ProjectMemberService

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_ACTOR_ID = uuid4()
_OTHER_ID = uuid4()
_PROJECT_ID = uuid4()
_MEMBER_ID = uuid4()


def _make_member(
    member_id: UUID | None = None,
    user_id: UUID | None = None,
    project_id: UUID | None = None,
    role: ProjectRole = ProjectRole.MEMBER,
) -> ProjectMember:
    """Build a ProjectMember ORM instance for use as a mock return value."""
    resolved_user_id = user_id or _ACTOR_ID
    member = mock.MagicMock(spec=ProjectMember)
    member.id = member_id or _MEMBER_ID
    member.project_id = project_id or _PROJECT_ID
    member.user_id = resolved_user_id
    member.role = role
    member.created_at = datetime.now(UTC)
    member.updated_at = datetime.now(UTC)
    member.user = SimpleNamespace(
        id=resolved_user_id,
        username="owner",
        email="owner@example.com",
    )
    return member


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_member_repo():
    """A mock ProjectMemberRepository with async methods returning defaults."""
    repo = mock.AsyncMock(spec=ProjectMemberRepository)
    repo.get_by_project.return_value = ([_make_member()], 1)
    repo.get_by_project_and_user.return_value = _make_member()
    repo.create.return_value = _make_member()
    repo.update.return_value = _make_member()
    return repo


@pytest.fixture
def mock_project_repo():
    """A mock ProjectRepository for project existence checks."""
    repo = mock.AsyncMock()
    repo.get_by_id.return_value = mock.MagicMock()
    return repo


@pytest.fixture
def service(mock_member_repo, mock_project_repo):
    """A ProjectMemberService with mocked repositories and session."""
    session = mock.AsyncMock()
    settings = mock.MagicMock()
    svc = ProjectMemberService(session, settings)
    svc._members = mock_member_repo
    svc._projects = mock_project_repo
    svc._session = session
    return svc


# ---------------------------------------------------------------------------
# list_members
# ---------------------------------------------------------------------------


class TestListMembers:
    """list_members delegates filtering/pagination to the repository."""

    @pytest.mark.asyncio
    async def test_empty(self, service, mock_member_repo, mock_project_repo) -> None:
        """When no members exist, the response has an empty items list."""
        mock_member_repo.get_by_project_and_user.return_value = _make_member()
        mock_member_repo.get_by_project.return_value = ([], 0)

        result = await service.list_members(user_id=_ACTOR_ID, project_id=_PROJECT_ID)

        assert result.items == []
        assert result.total == 0
        assert result.total_pages == 1

    @pytest.mark.asyncio
    async def test_paginated_result(
        self, service, mock_member_repo, mock_project_repo
    ) -> None:
        """A single member is returned with correct pagination metadata."""
        mock_member_repo.get_by_project_and_user.return_value = _make_member()
        mock_member_repo.get_by_project.return_value = ([_make_member()], 1)

        result = await service.list_members(
            user_id=_ACTOR_ID, project_id=_PROJECT_ID, page=1, page_size=20
        )

        assert len(result.items) == 1
        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 20
        assert result.total_pages == 1

    @pytest.mark.asyncio
    async def test_pagination_pass_through(
        self, service, mock_member_repo, mock_project_repo
    ) -> None:
        """Pagination parameters are forwarded to the repository."""
        mock_member_repo.get_by_project_and_user.return_value = _make_member()
        mock_member_repo.get_by_project.return_value = ([], 0)

        await service.list_members(
            user_id=_ACTOR_ID,
            project_id=_PROJECT_ID,
            page=2,
            page_size=10,
        )

        mock_member_repo.get_by_project.assert_awaited_once_with(
            project_id=_PROJECT_ID,
            page=2,
            page_size=10,
        )

    @pytest.mark.asyncio
    async def test_project_not_found(
        self, service, mock_member_repo, mock_project_repo
    ) -> None:
        """ProjectNotFoundError is raised when the project does not exist."""
        mock_project_repo.get_by_id.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await service.list_members(user_id=_ACTOR_ID, project_id=_PROJECT_ID)

    @pytest.mark.asyncio
    async def test_access_denied(
        self, service, mock_member_repo, mock_project_repo
    ) -> None:
        """ProjectNotFoundError is raised for a non-member."""
        mock_member_repo.get_by_project_and_user.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await service.list_members(user_id=_OTHER_ID, project_id=_PROJECT_ID)


# ---------------------------------------------------------------------------
# add_member
# ---------------------------------------------------------------------------


class TestAddMember:
    """add_member requires ADMIN/OWNER and creates a new membership record."""

    @pytest.mark.asyncio
    async def test_success(self, service, mock_member_repo, mock_project_repo) -> None:
        """Member is created and committed when actor has ADMIN role."""
        mock_member_repo.get_by_project_and_user.side_effect = (
            _make_member(role=ProjectRole.ADMIN),  # actor membership
            None,  # target not already a member
        )
        payload = MemberAddRequest(user_id=_OTHER_ID, role=ProjectRole.MEMBER)

        result = await service.add_member(
            actor_id=_ACTOR_ID,
            project_id=_PROJECT_ID,
            payload=payload,
        )

        mock_member_repo.create.assert_awaited_once_with(
            project_id=_PROJECT_ID,
            user_id=_OTHER_ID,
            role=ProjectRole.MEMBER,
        )
        service._session.commit.assert_awaited_once()
        assert result.user_id == _ACTOR_ID

    @pytest.mark.asyncio
    async def test_already_exists(
        self, service, mock_member_repo, mock_project_repo
    ) -> None:
        """MemberAlreadyExistsError is raised when user is already a member."""
        from app.core.exceptions import MemberAlreadyExistsError

        mock_member_repo.get_by_project_and_user.side_effect = (
            _make_member(role=ProjectRole.OWNER),  # actor membership
            _make_member(user_id=_OTHER_ID),  # target already exists
        )
        payload = MemberAddRequest(user_id=_OTHER_ID)

        with pytest.raises(MemberAlreadyExistsError):
            await service.add_member(
                actor_id=_ACTOR_ID,
                project_id=_PROJECT_ID,
                payload=payload,
            )

    @pytest.mark.asyncio
    async def test_insufficient_permission(
        self, service, mock_member_repo, mock_project_repo
    ) -> None:
        """InsufficientPermissionError is raised when actor is only a MEMBER."""
        mock_member_repo.get_by_project_and_user.return_value = _make_member(
            role=ProjectRole.MEMBER
        )
        payload = MemberAddRequest(user_id=_OTHER_ID)

        with pytest.raises(InsufficientPermissionError):
            await service.add_member(
                actor_id=_ACTOR_ID,
                project_id=_PROJECT_ID,
                payload=payload,
            )

    @pytest.mark.asyncio
    async def test_project_not_found(
        self, service, mock_member_repo, mock_project_repo
    ) -> None:
        """ProjectNotFoundError is raised when the project does not exist."""
        mock_project_repo.get_by_id.return_value = None
        payload = MemberAddRequest(user_id=_OTHER_ID)

        with pytest.raises(ProjectNotFoundError):
            await service.add_member(
                actor_id=_ACTOR_ID,
                project_id=_PROJECT_ID,
                payload=payload,
            )


# ---------------------------------------------------------------------------
# update_member_role
# ---------------------------------------------------------------------------


class TestUpdateMemberRole:
    """update_member_role requires OWNER and changes the member's role."""

    @pytest.mark.asyncio
    async def test_success(self, service, mock_member_repo, mock_project_repo) -> None:
        """Role is updated and committed when actor is OWNER."""
        mock_member_repo.get_by_project_and_user.side_effect = (
            _make_member(role=ProjectRole.OWNER),  # actor
            _make_member(user_id=_OTHER_ID),  # target
        )
        payload = MemberRoleUpdateRequest(role=ProjectRole.ADMIN)

        result = await service.update_member_role(
            actor_id=_ACTOR_ID,
            project_id=_PROJECT_ID,
            target_user_id=_OTHER_ID,
            payload=payload,
        )

        mock_member_repo.update.assert_awaited_once()
        service._session.commit.assert_awaited_once()
        assert result.role == ProjectRole.MEMBER

    @pytest.mark.asyncio
    async def test_target_not_found(
        self, service, mock_member_repo, mock_project_repo
    ) -> None:
        """MemberNotFoundError is raised when target user is not a member."""
        mock_member_repo.get_by_project_and_user.side_effect = (
            _make_member(role=ProjectRole.OWNER),  # actor
            None,  # target not found
        )
        payload = MemberRoleUpdateRequest(role=ProjectRole.ADMIN)

        with pytest.raises(MemberNotFoundError):
            await service.update_member_role(
                actor_id=_ACTOR_ID,
                project_id=_PROJECT_ID,
                target_user_id=_OTHER_ID,
                payload=payload,
            )

    @pytest.mark.asyncio
    async def test_insufficient_permission(
        self, service, mock_member_repo, mock_project_repo
    ) -> None:
        """InsufficientPermissionError when actor is not OWNER."""
        mock_member_repo.get_by_project_and_user.return_value = _make_member(
            role=ProjectRole.ADMIN
        )
        payload = MemberRoleUpdateRequest(role=ProjectRole.MEMBER)

        with pytest.raises(InsufficientPermissionError):
            await service.update_member_role(
                actor_id=_ACTOR_ID,
                project_id=_PROJECT_ID,
                target_user_id=_OTHER_ID,
                payload=payload,
            )


# ---------------------------------------------------------------------------
# remove_member
# ---------------------------------------------------------------------------


class TestRemoveMember:
    """remove_member requires ADMIN/OWNER and removes the target member."""

    @pytest.mark.asyncio
    async def test_success_admin_removes_member(
        self, service, mock_member_repo, mock_project_repo
    ) -> None:
        """Member is deleted and committed when ADMIN removes a MEMBER."""
        mock_member_repo.get_by_project_and_user.side_effect = (
            _make_member(role=ProjectRole.ADMIN),  # actor (admin)
            _make_member(user_id=_OTHER_ID, role=ProjectRole.MEMBER),  # target
        )

        await service.remove_member(
            actor_id=_ACTOR_ID,
            project_id=_PROJECT_ID,
            target_user_id=_OTHER_ID,
        )

        mock_member_repo.delete.assert_awaited_once()
        service._session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_target_not_found(
        self, service, mock_member_repo, mock_project_repo
    ) -> None:
        """MemberNotFoundError when target is not a member."""
        mock_member_repo.get_by_project_and_user.side_effect = (
            _make_member(role=ProjectRole.OWNER),  # actor
            None,  # target
        )

        with pytest.raises(MemberNotFoundError):
            await service.remove_member(
                actor_id=_ACTOR_ID,
                project_id=_PROJECT_ID,
                target_user_id=_OTHER_ID,
            )

    @pytest.mark.asyncio
    async def test_cannot_remove_owner(
        self, service, mock_member_repo, mock_project_repo
    ) -> None:
        """InsufficientPermissionError when trying to remove the OWNER."""
        mock_member_repo.get_by_project_and_user.side_effect = (
            _make_member(role=ProjectRole.ADMIN),  # actor
            _make_member(user_id=_OTHER_ID, role=ProjectRole.OWNER),  # target
        )

        with pytest.raises(InsufficientPermissionError, match="Cannot remove"):
            await service.remove_member(
                actor_id=_ACTOR_ID,
                project_id=_PROJECT_ID,
                target_user_id=_OTHER_ID,
            )

    @pytest.mark.asyncio
    async def test_admin_cannot_remove_admin(
        self, service, mock_member_repo, mock_project_repo
    ) -> None:
        """InsufficientPermissionError when ADMIN tries to remove another ADMIN."""
        mock_member_repo.get_by_project_and_user.side_effect = (
            _make_member(role=ProjectRole.ADMIN),  # actor
            _make_member(user_id=_OTHER_ID, role=ProjectRole.ADMIN),  # target
        )

        with pytest.raises(InsufficientPermissionError, match="admin"):
            await service.remove_member(
                actor_id=_ACTOR_ID,
                project_id=_PROJECT_ID,
                target_user_id=_OTHER_ID,
            )

    @pytest.mark.asyncio
    async def test_insufficient_permission_member(
        self, service, mock_member_repo, mock_project_repo
    ) -> None:
        """InsufficientPermissionError when actor is only a MEMBER."""
        mock_member_repo.get_by_project_and_user.return_value = _make_member(
            role=ProjectRole.MEMBER
        )

        with pytest.raises(InsufficientPermissionError):
            await service.remove_member(
                actor_id=_ACTOR_ID,
                project_id=_PROJECT_ID,
                target_user_id=_OTHER_ID,
            )
