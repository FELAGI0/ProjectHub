"""Business logic for project member management."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import (
    InsufficientPermissionError,
    MemberAlreadyExistsError,
    MemberNotFoundError,
)
from app.modules.project_members.authorization import require_project_membership
from app.modules.project_members.models import ProjectMember, ProjectRole
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.project_members.schemas import (
    MemberAddRequest,
    MemberResponse,
    MemberRoleUpdateRequest,
    PaginatedMembersResponse,
)
from app.modules.projects.repository import ProjectRepository


class ProjectMemberService:
    """Coordinates member CRUD with role-based permission enforcement."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._members = ProjectMemberRepository(session)
        self._projects = ProjectRepository(session)

    async def list_members(
        self,
        *,
        user_id: UUID,
        project_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedMembersResponse:
        """Return a paginated list of project members.

        The calling user must be a member of the project.
        """

        await self._verify_project_membership(user_id, project_id)

        members, total = await self._members.get_by_project(
            project_id=project_id,
            page=page,
            page_size=page_size,
        )
        total_pages = -(-total // page_size) if total > 0 else 1

        return PaginatedMembersResponse(
            items=[MemberResponse.model_validate(m) for m in members],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def add_member(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        payload: MemberAddRequest,
    ) -> MemberResponse:
        """Add a new member to a project.

        The actor must have ADMIN or OWNER role.
        """

        await self._verify_project_membership(
            actor_id, project_id, min_role=ProjectRole.ADMIN
        )

        existing = await self._members.get_by_project_and_user(
            project_id, payload.user_id
        )
        if existing is not None:
            raise MemberAlreadyExistsError()

        member = await self._members.create(
            project_id=project_id,
            user_id=payload.user_id,
            role=payload.role,
        )
        await self._session.commit()
        return MemberResponse.model_validate(member)

    async def update_member_role(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        target_user_id: UUID,
        payload: MemberRoleUpdateRequest,
    ) -> MemberResponse:
        """Change a member's role.

        Only the OWNER can change roles.
        """

        await self._verify_project_membership(
            actor_id, project_id, min_role=ProjectRole.OWNER
        )

        member = await self._members.get_by_project_and_user(
            project_id, target_user_id
        )
        if member is None:
            raise MemberNotFoundError()

        member = await self._members.update(member, role=payload.role)
        await self._session.commit()
        return MemberResponse.model_validate(member)

    async def remove_member(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        target_user_id: UUID,
    ) -> None:
        """Remove a member from a project.

        The actor must have ADMIN or OWNER role.
        An OWNER cannot be removed by anyone.
        """

        actor_membership = await self._verify_project_membership(
            actor_id, project_id, min_role=ProjectRole.ADMIN
        )

        target_member = await self._members.get_by_project_and_user(
            project_id, target_user_id
        )
        if target_member is None:
            raise MemberNotFoundError()

        if target_member.role == ProjectRole.OWNER:
            raise InsufficientPermissionError("Cannot remove the project owner.")

        if (
            actor_membership.role == ProjectRole.ADMIN
            and target_member.role == ProjectRole.ADMIN
        ):
            raise InsufficientPermissionError(
                "An admin cannot remove another admin."
            )

        await self._members.delete(target_member)
        await self._session.commit()

    async def verify_membership(
        self,
        user_id: UUID,
        project_id: UUID,
        min_role: ProjectRole | None = None,
    ) -> ProjectMember:
        """Check that user is a member of the project and optionally has a minimum role.

        Returns the membership record if checks pass.
        Raises ProjectNotFoundError / ProjectAccessDeniedError otherwise.
        """

        return await self._verify_project_membership(
            user_id, project_id, min_role=min_role
        )

    async def _verify_project_membership(
        self,
        user_id: UUID,
        project_id: UUID,
        min_role: ProjectRole | None = None,
    ) -> ProjectMember:
        """Core membership check shared across all operations."""
        _, membership = await require_project_membership(
            self._projects, self._members, user_id, project_id, min_role
        )
        return membership