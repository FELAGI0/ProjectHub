"""Persistence operations for the project_members module."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.project_members.models import ProjectMember, ProjectRole


class ProjectMemberRepository:
    """Database access methods for project memberships."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_project(
        self,
        *,
        project_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ProjectMember], int]:
        """Return a paginated list of members for a project."""

        stmt = (
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .order_by(ProjectMember.created_at.asc())
        )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self._session.execute(stmt)
        members = list(result.scalars().all())

        return members, total

    async def get_by_project_and_user(
        self,
        project_id: UUID,
        user_id: UUID,
    ) -> ProjectMember | None:
        """Return a specific member record or None."""

        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        project_id: UUID,
        user_id: UUID,
        role: ProjectRole = ProjectRole.MEMBER,
    ) -> ProjectMember:
        """Add a new member to the current transaction."""

        member = ProjectMember(
            project_id=project_id,
            user_id=user_id,
            role=role,
        )
        self._session.add(member)
        await self._session.flush()
        return member

    async def update(
        self,
        member: ProjectMember,
        *,
        role: ProjectRole,
    ) -> ProjectMember:
        """Change a member's role within the current transaction."""

        member.role = role
        await self._session.flush()
        return member

    async def delete(self, member: ProjectMember) -> None:
        """Remove a member within the current transaction."""

        await self._session.delete(member)
        await self._session.flush()
