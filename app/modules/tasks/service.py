"""Business logic for task management."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import (
    ProjectAccessDeniedError,
    ProjectNotFoundError,
    TaskNotFoundError,
)
from app.modules.projects.repository import ProjectRepository
from app.modules.tasks.models import Task, TaskPriority, TaskStatus
from app.modules.tasks.repository import TaskRepository
from app.modules.tasks.schemas import (
    PaginatedTasksResponse,
    TaskCreateRequest,
    TaskResponse,
    TaskUpdateRequest,
)


class TaskService:
    """Coordinates task CRUD with project-ownership enforcement."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._tasks = TaskRepository(session)
        self._projects = ProjectRepository(session)

    async def list_tasks(
        self,
        *,
        user_id: UUID,
        project_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        search: str | None = None,
    ) -> PaginatedTasksResponse:
        """Return a paginated list of tasks for a project the user owns."""

        await self._verify_project_ownership(user_id, project_id)

        tasks, total = await self._tasks.get_project_tasks(
            project_id=project_id,
            page=page,
            page_size=page_size,
            status=status,
            priority=priority,
            search=search,
        )
        total_pages = -(-total // page_size) if total > 0 else 1

        return PaginatedTasksResponse(
            items=[TaskResponse.model_validate(t) for t in tasks],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_task(
        self,
        user_id: UUID,
        project_id: UUID,
        payload: TaskCreateRequest,
    ) -> TaskResponse:
        """Create a new task in a project the user owns."""

        await self._verify_project_ownership(user_id, project_id)

        task = await self._tasks.create(
            project_id=project_id,
            title=payload.title,
            description=payload.description,
            status=payload.status,
            priority=payload.priority,
            due_date=payload.due_date,
        )
        await self._session.commit()
        return TaskResponse.model_validate(task)

    async def get_task(
        self,
        user_id: UUID,
        task_id: UUID,
    ) -> TaskResponse:
        """Return a task if the calling user owns its parent project."""

        task = await self._get_accessible_task(user_id, task_id)
        return TaskResponse.model_validate(task)

    async def update_task(
        self,
        user_id: UUID,
        task_id: UUID,
        payload: TaskUpdateRequest,
    ) -> TaskResponse:
        """Update fields on a task whose parent project the user owns."""

        task = await self._get_accessible_task(user_id, task_id)

        task = await self._tasks.update(
            task,
            title=payload.title,
            description=payload.description,
            status=payload.status,
            priority=payload.priority,
            due_date=payload.due_date,
        )
        await self._session.commit()
        return TaskResponse.model_validate(task)

    async def delete_task(
        self,
        user_id: UUID,
        task_id: UUID,
    ) -> None:
        """Delete a task if the calling user owns its parent project."""

        task = await self._get_accessible_task(user_id, task_id)
        await self._tasks.delete(task)
        await self._session.commit()

    async def _verify_project_ownership(self, user_id: UUID, project_id: UUID) -> None:
        """Fetch a project and verify ownership.

        Raises ProjectNotFoundError (404) if the project does not exist and
        ProjectAccessDeniedError (403) if it belongs to another user.
        """

        project = await self._projects.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError()
        if project.owner_id != user_id:
            raise ProjectAccessDeniedError()

    async def _get_accessible_task(self, user_id: UUID, task_id: UUID) -> Task:
        """Fetch a task and verify the user owns its parent project.

        Raises TaskNotFoundError (404) if the task does not exist,
        ProjectNotFoundError (404) if the parent project is gone, and
        ProjectAccessDeniedError (403) if the project belongs to another user.
        """

        task = await self._tasks.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError()
        await self._verify_project_ownership(user_id, task.project_id)
        return task
