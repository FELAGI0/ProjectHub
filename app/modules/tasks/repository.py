"""Persistence operations for the tasks module."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tasks.models import Task, TaskPriority, TaskStatus


class TaskRepository:
    """Database access methods for tasks."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, task_id: UUID) -> Task | None:
        """Return a task by its identifier."""

        return await self._session.get(Task, task_id)

    async def get_project_tasks(
        self,
        *,
        project_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        search: str | None = None,
    ) -> tuple[list[Task], int]:
        """Return a paginated, filtered list of tasks for a project.

        Returns the task list and the total matching count.
        """

        stmt = select(Task).where(Task.project_id == project_id)

        if status is not None:
            stmt = stmt.where(Task.status.is_(status))
        if priority is not None:
            stmt = stmt.where(Task.priority.is_(priority))
        if search is not None:
            pattern = f"%{search}%"
            stmt = stmt.where(Task.title.ilike(pattern))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(Task.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self._session.execute(stmt)
        tasks = list(result.scalars().all())

        return tasks, total

    async def create(
        self,
        *,
        project_id: UUID,
        title: str,
        description: str | None = None,
        status: TaskStatus = TaskStatus.TODO,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: datetime | None = None,
    ) -> Task:
        """Add a new task to the current transaction."""

        task = Task(
            project_id=project_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
        )
        self._session.add(task)
        await self._session.flush()
        return task

    async def update(
        self,
        task: Task,
        *,
        title: str | None = None,
        description: str | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        due_date: datetime | None = None,
    ) -> Task:
        """Mutate fields on an existing task within the current transaction."""

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority
        if due_date is not None:
            task.due_date = due_date
        await self._session.flush()
        return task

    async def delete(self, task: Task) -> None:
        """Remove a task within the current transaction."""

        await self._session.delete(task)
        await self._session.flush()
