"""Business logic for project management."""

import logging
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import ConflictError, DomainError
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

logger = logging.getLogger(__name__)


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
        await self._session.refresh(project)
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

    async def transfer_ownership(
        self,
        user_id: UUID,
        project_id: UUID,
        new_owner_id: UUID,
    ) -> None:
        """Transfer project ownership to another project member.

        Requirements:
        - Caller must be the current OWNER.
        - New owner must be an existing project member.
        - Caller cannot transfer to themselves.
        - Old owner becomes ADMIN after transfer.
        """

        project, caller_member = await require_project_membership(
            projects_repo=self._projects,
            members_repo=self._members,
            user_id=user_id,
            project_id=project_id,
            min_role=ProjectRole.OWNER,
        )

        if new_owner_id == user_id:
            raise DomainError("Cannot transfer ownership to yourself")

        new_owner_member = await self._members.get_by_project_and_user(
            project_id, new_owner_id
        )
        if new_owner_member is None:
            raise DomainError("User is not a project member")

        caller_member.role = ProjectRole.ADMIN
        new_owner_member.role = ProjectRole.OWNER
        project.owner_id = new_owner_id

        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise ConflictError(
                "Ownership was changed concurrently, please retry"
            ) from exc

        logger.info(
            "Project %s ownership transferred from %s to %s",
            project_id,
            user_id,
            new_owner_id,
        )

    async def _verify_project_access(
        self,
        user_id: UUID,
        project_id: UUID,
        min_role: ProjectRole | None = None,
    ) -> Project:
        """Fetch a project and verify the user has a minimum role.

        Raises ProjectNotFoundError (404) if the project does not exist or the user
        is not a member, and InsufficientPermissionError (403) if the user's role
        is too low.
        """

        project, _ = await require_project_membership(
            self._projects, self._members, user_id, project_id, min_role
        )
        return project
