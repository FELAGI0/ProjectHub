"""Project member management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.core.config import get_settings
from app.db.session import get_db_session
from app.modules.project_members.schemas import (
    MemberAddRequest,
    MemberResponse,
    MemberRoleUpdateRequest,
    PaginatedMembersResponse,
)
from app.modules.project_members.service import ProjectMemberService

router = APIRouter(prefix="/projects/{project_id}/members", tags=["Project Members"])


def get_member_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProjectMemberService:
    """Create a member service bound to the current request session."""

    return ProjectMemberService(session, get_settings())


@router.get(
    "",
    response_model=PaginatedMembersResponse,
    summary="List project members",
    description=(
        "Return a paginated list of members for a project. "
        "The caller must be a member of the project."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Caller is not a member of this project."
        },
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
    },
)
async def list_members(
    project_id: UUID,
    current_user: CurrentUser,
    service: Annotated[ProjectMemberService, Depends(get_member_service)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedMembersResponse:
    """List members of a project."""
    return await service.list_members(
        user_id=current_user.id,
        project_id=project_id,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a project member",
    description="Add a user to a project. The caller must have ADMIN or OWNER role.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Caller does not have permission to add members."
        },
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
        status.HTTP_409_CONFLICT: {
            "description": "User is already a member of this project."
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation error in request body."
        },
    },
)
async def add_member(
    project_id: UUID,
    payload: MemberAddRequest,
    current_user: CurrentUser,
    service: Annotated[ProjectMemberService, Depends(get_member_service)],
) -> MemberResponse:
    """Add a new member to a project."""

    return await service.add_member(
        actor_id=current_user.id,
        project_id=project_id,
        payload=payload,
    )


@router.patch(
    "/{user_id}",
    response_model=MemberResponse,
    summary="Update a member's role",
    description="Change the role of a project member. Only the OWNER can change roles.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Caller does not have permission to change roles."
        },
        status.HTTP_404_NOT_FOUND: {"description": "Member not found."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation error in request body."
        },
    },
)
async def update_member_role(
    project_id: UUID,
    user_id: UUID,
    payload: MemberRoleUpdateRequest,
    current_user: CurrentUser,
    service: Annotated[ProjectMemberService, Depends(get_member_service)],
) -> MemberResponse:
    """Update a member's role."""

    return await service.update_member_role(
        actor_id=current_user.id,
        project_id=project_id,
        target_user_id=user_id,
        payload=payload,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a project member",
    description=(
        "Remove a user from a project. The caller must have ADMIN or "
        "OWNER role. The OWNER cannot be removed."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Caller does not have permission to remove members."
        },
        status.HTTP_404_NOT_FOUND: {"description": "Member not found."},
    },
)
async def remove_member(
    project_id: UUID,
    user_id: UUID,
    current_user: CurrentUser,
    service: Annotated[ProjectMemberService, Depends(get_member_service)],
) -> None:
    """Remove a member from a project."""

    await service.remove_member(
        actor_id=current_user.id,
        project_id=project_id,
        target_user_id=user_id,
    )