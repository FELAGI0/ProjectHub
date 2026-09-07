"""Shared authorization helpers for project membership checks."""

from uuid import UUID

from app.core.exceptions import (
    InsufficientPermissionError,
    ProjectAccessDeniedError,
    ProjectNotFoundError,
)
from app.modules.project_members.models import ProjectRole


async def require_project_membership(
    projects_repo,
    members_repo,
    user_id: UUID,
    project_id: UUID,
    min_role: ProjectRole | None = None,
):
    """Ensure the project exists and the user is a member with optional min_role.

    Returns tuple(project, membership). Raises domain errors on failure.
    """

    project = await projects_repo.get_by_id(project_id)
    if project is None:
        raise ProjectNotFoundError()

    membership = await members_repo.get_by_project_and_user(project_id, user_id)
    if membership is None:
        raise ProjectAccessDeniedError()

    if min_role is not None and membership.role.level < min_role.level:
        raise InsufficientPermissionError()

    return project, membership
