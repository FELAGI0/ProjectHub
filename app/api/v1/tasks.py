"""Task management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.core.config import get_settings
from app.db.session import get_db_session
from app.modules.tasks.models import TaskPriority, TaskStatus
from app.modules.tasks.schemas import (
    PaginatedTasksResponse,
    TaskCreateRequest,
    TaskResponse,
    TaskUpdateRequest,
)
from app.modules.tasks.service import TaskService

router = APIRouter(prefix="", tags=["Tasks"])


def get_task_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TaskService:
    """Create a task service bound to the current request session."""

    return TaskService(session, get_settings())


# ---------------------------------------------------------------------------
# Nested under /projects/{project_id}/tasks
# ---------------------------------------------------------------------------


@router.get(
    "/projects/{project_id}/tasks",
    response_model=PaginatedTasksResponse,
    summary="List tasks for a project",
    description=(
        "Return a paginated list of tasks belonging to a project owned by the"
        " authenticated user. Supports optional status, priority and search"
        " filtering."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Project exists but is not owned by the caller."
        },
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
    },
)
async def list_tasks(
    project_id: UUID,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends(get_task_service)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    search: str | None = Query(default=None, max_length=200),
) -> PaginatedTasksResponse:
    """List tasks for a project."""

    return await service.list_tasks(
        user_id=current_user.id,
        project_id=project_id,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        search=search,
    )


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
    description="Create a new task in a project owned by the authenticated user.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Project exists but is not owned by the caller."
        },
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Validation error in request body."
        },
    },
)
async def create_task(
    project_id: UUID,
    payload: TaskCreateRequest,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    """Create a new task."""

    return await service.create_task(current_user.id, project_id, payload)


# ---------------------------------------------------------------------------
# Top-level under /tasks/{task_id}
# ---------------------------------------------------------------------------


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID",
    description=(
        "Return a single task if the authenticated user owns its parent project."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ("Task or its parent project belongs to another user.")
        },
        status.HTTP_404_NOT_FOUND: {"description": "Task not found."},
    },
)
async def get_task(
    task_id: UUID,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    """Get a task by ID."""

    return await service.get_task(current_user.id, task_id)


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    description=(
        "Update a task. Only users who own the parent project can update its tasks."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ("Task or its parent project belongs to another user.")
        },
        status.HTTP_404_NOT_FOUND: {"description": "Task not found."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Validation error in request body."
        },
    },
)
async def update_task(
    task_id: UUID,
    payload: TaskUpdateRequest,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    """Update a task."""

    return await service.update_task(current_user.id, task_id, payload)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description=(
        "Delete a task permanently. Only users who own the parent project can"
        " delete its tasks."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ("Task or its parent project belongs to another user.")
        },
        status.HTTP_404_NOT_FOUND: {"description": "Task not found."},
    },
)
async def delete_task(
    task_id: UUID,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends(get_task_service)],
) -> None:
    """Delete a task."""

    await service.delete_task(current_user.id, task_id)
