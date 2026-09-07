"""Persistence operations for the projects module."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.project_members.models import ProjectMember
from app.modules.projects.models import Project


class ProjectRepository:
    """Database access methods for projects."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_member_projects(
        self,
        *,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Project], int]:
        """Return a paginated, filtered list of projects where a user is a member.

        Returns the project list and the total matching count.
        """

        stmt = (
            select(Project)
            .join(ProjectMember, Project.id == ProjectMember.project_id)
            .where(ProjectMember.user_id == user_id)
        )

        if search is not None:
            pattern = f"%{search}%"
            stmt = stmt.where(Project.name.ilike(pattern))
        if is_active is not None:
            stmt = stmt.where(Project.is_active.is_(is_active))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(Project.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self._session.execute(stmt)
        projects = list(result.scalars().all())

        return projects, total

    async def get_by_id(self, project_id: UUID) -> Project | None:
        """Return a project by its identifier."""

        return await self._session.get(Project, project_id)

    async def get_owned(
        self,
        *,
        owner_id: UUID,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Project], int]:
        """Return a paginated, filtered list of projects owned by a user.

        Returns the project list and the total matching count.
        """

        stmt = select(Project).where(Project.owner_id == owner_id)

        if search is not None:
            pattern = f"%{search}%"
            stmt = stmt.where(Project.name.ilike(pattern))
        if is_active is not None:
            stmt = stmt.where(Project.is_active.is_(is_active))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(Project.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self._session.execute(stmt)
        projects = list(result.scalars().all())

        return projects, total

    async def create(
        self,
        *,
        owner_id: UUID,
        name: str,
        description: str | None = None,
    ) -> Project:
        """Add a new project to the current transaction."""

        project = Project(
            owner_id=owner_id,
            name=name,
            description=description,
        )
        self._session.add(project)
        await self._session.flush()
        return project

    async def update(
        self,
        project: Project,
        *,
        name: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
    ) -> Project:
        """Mutate fields on an existing project within the current transaction."""

        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if is_active is not None:
            project.is_active = is_active
        await self._session.flush()
        return project

    async def delete(self, project: Project) -> None:
        """Remove a project within the current transaction."""

        await self._session.delete(project)
        await self._session.flush()
