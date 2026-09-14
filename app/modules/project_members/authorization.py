"""Shared authorization helpers for project membership checks."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from app.core.exceptions import (
    InsufficientPermissionError,
    ProjectNotFoundError,
)
from app.modules.project_members.models import ProjectRole

if TYPE_CHECKING:
    from app.modules.project_members.models import ProjectMember
    from app.modules.project_members.repository import ProjectMemberRepository
    from app.modules.projects.models import Project
    from app.modules.projects.repository import ProjectRepository


async def require_project_membership(
    projects_repo: ProjectRepository,
    members_repo: ProjectMemberRepository,
    user_id: UUID,
    project_id: UUID,
    min_role: ProjectRole | None = None,
) -> tuple[Project, ProjectMember]:
    """Ensure the project exists and the user is a member with optional min_role.

    Args:
        projects_repo: ProjectRepository instance for project lookups.
        members_repo: ProjectMemberRepository instance for membership checks.
        user_id: UUID of the user to check.
        project_id: UUID of the project to check.
        min_role: Optional minimum role required. If None, only membership is
                  checked. Otherwise raises InsufficientPermissionError if the
                  user's role level is below min_role.

    Returns:
        Tuple of (project, membership). Raises domain errors on failure:
        - ProjectNotFoundError (404) if project does not exist or user is not a member
        - InsufficientPermissionError (403) if min_role is set and user's role
          is too low
    """

    project = await projects_repo.get_by_id(project_id)
    if project is None:
        raise ProjectNotFoundError()

    membership = await members_repo.get_by_project_and_user(project_id, user_id)
    if membership is None:
        raise ProjectNotFoundError()

    if min_role is not None and membership.role.level < min_role.level:
        raise InsufficientPermissionError()

    return project, membership
