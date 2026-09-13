"""Project management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.core.config import get_settings
from app.db.session import get_db_session
from app.modules.projects.schemas import (
    PaginatedProjectsResponse,
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
)
from app.modules.projects.service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


def get_project_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProjectService:
    """Create a project service bound to the current request session."""

    return ProjectService(session, get_settings())


@router.get(
    "/",
    response_model=PaginatedProjectsResponse,
    summary="List user's projects",
    description=(
        "Return a paginated list of projects where the authenticated user is a"
        " member. Supports optional search and active-status filtering."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token."
        },
    },
)
async def list_projects(
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends(get_project_service)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=100),
    is_active: bool | None = None,
) -> PaginatedProjectsResponse:
    """List projects the current user is a member of."""

    return await service.list_projects(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active,
    )


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
    description="Create a new project owned by the authenticated user.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Validation error in request body."
        },
    },
)
async def create_project(
    payload: ProjectCreateRequest,
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    """Create a new project."""

    return await service.create_project(current_user.id, payload)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get a project by ID",
    description="Return a single project if the authenticated user is a member.",
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
async def get_project(
    project_id: UUID,
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    """Get a project by ID."""

    return await service.get_project(current_user.id, project_id)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project",
    description=("Partially update a project. Requires ADMIN or OWNER role."),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Caller does not have sufficient permissions."
        },
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Validation error in request body."
        },
    },
)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdateRequest,
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    """Update a project."""

    return await service.update_project(current_user.id, project_id, payload)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
    description=(
        "Delete a project permanently. Only the OWNER can delete their project."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Caller does not have sufficient permissions."
        },
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
    },
)
async def delete_project(
    project_id: UUID,
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> None:
    """Delete a project."""

    await service.delete_project(current_user.id, project_id)
