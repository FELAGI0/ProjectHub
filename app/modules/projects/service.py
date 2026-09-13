"""Business logic for project management."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.modules.project_members.authorization import require_project_membership
from app.modules.project_members.models import ProjectRole
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.projects.models import Project
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schemas import (
    PaginatedProjectsResponse,
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
)


class ProjectService:
    """Coordinates project CRUD with membership-based authorization."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._projects = ProjectRepository(session)
        self._members = ProjectMemberRepository(session)

    async def list_projects(
        self,
        *,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> PaginatedProjectsResponse:
        """Return a paginated list of projects the user is a member of."""

        projects, total = await self._projects.get_member_projects(
            user_id=user_id,
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active,
        )
        total_pages = -(-total // page_size) if total > 0 else 1

        return PaginatedProjectsResponse(
            items=[ProjectResponse.model_validate(p) for p in projects],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_project(
        self,
        owner_id: UUID,
        payload: ProjectCreateRequest,
    ) -> ProjectResponse:
        """Create a new project owned by the specified user.

        Automatically creates an OWNER membership record for the creator.
        """

        project = await self._projects.create(
            owner_id=owner_id,
            name=payload.name,
            description=payload.description,
        )
        await self._members.create(
            project_id=project.id,
            user_id=owner_id,
            role=ProjectRole.OWNER,
        )
        await self._session.commit()
        return ProjectResponse.model_validate(project)

    async def get_project(
        self,
        user_id: UUID,
        project_id: UUID,
    ) -> ProjectResponse:
        """Return a project if the calling user is a member."""

        project = await self._verify_project_access(user_id, project_id)
        return ProjectResponse.model_validate(project)

    async def update_project(
        self,
        user_id: UUID,
        project_id: UUID,
        payload: ProjectUpdateRequest,
    ) -> ProjectResponse:
        """Update fields on a project. Requires ADMIN or OWNER role."""

        project = await self._verify_project_access(
            user_id, project_id, min_role=ProjectRole.ADMIN
        )

        project = await self._projects.update(
            project,
            name=payload.name,
            description=payload.description,
            is_active=payload.is_active,
        )
        await self._session.commit()
        return ProjectResponse.model_validate(project)

    async def delete_project(
        self,
        user_id: UUID,
        project_id: UUID,
    ) -> None:
        """Delete a project. Requires OWNER role."""

        project = await self._verify_project_access(
            user_id, project_id, min_role=ProjectRole.OWNER
        )
        await self._projects.delete(project)
        await self._session.commit()

    async def _verify_project_access(
        self,
        user_id: UUID,
        project_id: UUID,
        min_role: ProjectRole | None = None,
    ) -> Project:
        """Fetch a project and verify the user has a minimum role.

        Raises ProjectNotFoundError (404) if the project does not exist,
        ProjectAccessDeniedError (403) if the user is not a member, and
        InsufficientPermissionError (403) if the user's role is too low.
        """

        project, _ = await require_project_membership(
            self._projects, self._members, user_id, project_id, min_role
        )
        return project
