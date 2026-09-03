"""Business logic for project management."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import ProjectAccessDeniedError, ProjectNotFoundError
from app.modules.projects.models import Project
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schemas import (
    PaginatedProjectsResponse,
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
)


class ProjectService:
    """Coordinates project CRUD with ownership enforcement."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._projects = ProjectRepository(session)

    async def list_projects(
        self,
        *,
        owner_id: UUID,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> PaginatedProjectsResponse:
        """Return a paginated list of projects owned by a user."""

        projects, total = await self._projects.get_owned(
            owner_id=owner_id,
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
        """Create a new project owned by the specified user."""

        project = await self._projects.create(
            owner_id=owner_id,
            name=payload.name,
            description=payload.description,
        )
        await self._session.commit()
        return ProjectResponse.model_validate(project)

    async def get_project(
        self,
        user_id: UUID,
        project_id: UUID,
    ) -> ProjectResponse:
        """Return a project if the calling user owns it."""

        project = await self._get_owned_project(user_id, project_id)
        return ProjectResponse.model_validate(project)

    async def update_project(
        self,
        user_id: UUID,
        project_id: UUID,
        payload: ProjectUpdateRequest,
    ) -> ProjectResponse:
        """Update fields on an owned project."""

        project = await self._get_owned_project(user_id, project_id)

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
        """Delete a project if the calling user owns it."""

        project = await self._get_owned_project(user_id, project_id)
        await self._projects.delete(project)
        await self._session.commit()

    async def _get_owned_project(self, user_id: UUID, project_id: UUID) -> Project:
        """Fetch a project and verify ownership.

        Raises ProjectNotFoundError (404) if the project does not exist and
        ProjectAccessDeniedError (403) if it belongs to another user.
        """

        project = await self._projects.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError()
        if project.owner_id != user_id:
            raise ProjectAccessDeniedError()
        return project
