"""Unit tests for repository layers with database mocking."""

from datetime import UTC, datetime
from unittest import mock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.models import Project
from app.modules.projects.repository import ProjectRepository
from app.modules.tasks.models import Task, TaskPriority, TaskStatus
from app.modules.tasks.repository import TaskRepository
from app.modules.users.models import RefreshToken, User
from app.modules.users.repository import RefreshTokenRepository, UserRepository


class TestProjectRepository:
    """Tests for ProjectRepository methods."""

    @pytest.fixture
    def session(self):
        """Mock AsyncSession."""
        return mock.AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, session):
        """ProjectRepository instance."""
        return ProjectRepository(session)

    @pytest.mark.asyncio
    async def test_get_by_id(self, session, repo):
        """get_by_id returns project or None."""
        project_id = uuid4()
        project = Project(
            id=project_id,
            owner_id=uuid4(),
            name="Test",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        session.get.return_value = project

        result = await repo.get_by_id(project_id)

        assert result == project
        session.get.assert_called_once_with(Project, project_id)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, session, repo):
        """get_by_id returns None when not found."""
        session.get.return_value = None

        result = await repo.get_by_id(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_create(self, session, repo):
        """create adds project to session."""
        owner_id = uuid4()

        result = await repo.create(
            owner_id=owner_id,
            name="New Project",
            description="A project",
        )

        session.add.assert_called_once()
        session.flush.assert_called_once()
        assert result.owner_id == owner_id
        assert result.name == "New Project"
        assert result.description == "A project"

    @pytest.mark.asyncio
    async def test_update_all_fields(self, session, repo):
        """update modifies all project fields."""
        project = Project(
            id=uuid4(),
            owner_id=uuid4(),
            name="Old",
            description="Old desc",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        result = await repo.update(
            project,
            name="New",
            description="New desc",
            is_active=False,
        )

        assert result.name == "New"
        assert result.description == "New desc"
        assert result.is_active is False
        session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_partial_fields(self, session, repo):
        """update with partial fields only changes specified ones."""
        project = Project(
            id=uuid4(),
            owner_id=uuid4(),
            name="Original",
            description="Original desc",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        original_desc = project.description
        original_active = project.is_active

        result = await repo.update(project, name="Changed")

        assert result.name == "Changed"
        assert result.description == original_desc
        assert result.is_active == original_active

    @pytest.mark.asyncio
    async def test_delete(self, session, repo):
        """delete removes project from session."""
        project = Project(
            id=uuid4(),
            owner_id=uuid4(),
            name="Delete me",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        await repo.delete(project)

        session.delete.assert_called_once_with(project)
        session.flush.assert_called_once()


class TestTaskRepository:
    """Tests for TaskRepository methods."""

    @pytest.fixture
    def session(self):
        """Mock AsyncSession."""
        return mock.AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, session):
        """TaskRepository instance."""
        return TaskRepository(session)

    @pytest.mark.asyncio
    async def test_get_by_id(self, session, repo):
        """get_by_id returns task or None."""
        task_id = uuid4()
        task = Task(
            id=task_id,
            project_id=uuid4(),
            title="Test Task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        session.get.return_value = task

        result = await repo.get_by_id(task_id)

        assert result == task
        session.get.assert_called_once_with(Task, task_id)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, session, repo):
        """get_by_id returns None when not found."""
        session.get.return_value = None

        result = await repo.get_by_id(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_create(self, session, repo):
        """create adds task to session."""
        project_id = uuid4()

        result = await repo.create(
            project_id=project_id,
            title="New Task",
            description="A task",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            due_date=None,
        )

        session.add.assert_called_once()
        session.flush.assert_called_once()
        assert result.project_id == project_id
        assert result.title == "New Task"
        assert result.status == TaskStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_update_all_fields(self, session, repo):
        """update modifies all task fields."""
        task = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="Old",
            description="Old desc",
            status=TaskStatus.TODO,
            priority=TaskPriority.LOW,
            due_date=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        new_date = datetime.now(UTC)

        result = await repo.update(
            task,
            title="New",
            description="New desc",
            status=TaskStatus.DONE,
            priority=TaskPriority.HIGH,
            due_date=new_date,
        )

        assert result.title == "New"
        assert result.description == "New desc"
        assert result.status == TaskStatus.DONE
        assert result.priority == TaskPriority.HIGH
        assert result.due_date == new_date

    @pytest.mark.asyncio
    async def test_update_partial_fields(self, session, repo):
        """update with partial fields only changes specified ones."""
        task = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="Original",
            description="Original desc",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            due_date=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        original_desc = task.description
        original_status = task.status

        result = await repo.update(task, title="Changed", priority=TaskPriority.LOW)

        assert result.title == "Changed"
        assert result.description == original_desc
        assert result.status == original_status
        assert result.priority == TaskPriority.LOW

    @pytest.mark.asyncio
    async def test_delete(self, session, repo):
        """delete removes task from session."""
        task = Task(
            id=uuid4(),
            project_id=uuid4(),
            title="Delete me",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        await repo.delete(task)

        session.delete.assert_called_once_with(task)
        session.flush.assert_called_once()


class TestUserRepository:
    """Tests for UserRepository methods."""

    @pytest.fixture
    def session(self):
        """Mock AsyncSession."""
        return mock.AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, session):
        """UserRepository instance."""
        return UserRepository(session)

    @pytest.mark.asyncio
    async def test_get_by_id(self, session, repo):
        """get_by_id returns user or None."""
        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            password_hash="hash",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        session.get.return_value = user

        result = await repo.get_by_id(user_id)

        assert result == user
        session.get.assert_called_once_with(User, user_id)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, session, repo):
        """get_by_id returns None when not found."""
        session.get.return_value = None

        result = await repo.get_by_id(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_email(self, session, repo):
        """get_by_email queries by email address."""
        user = User(
            id=uuid4(),
            email="user@example.com",
            username="user",
            password_hash="hash",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_result = mock.Mock()
        mock_result.scalar_one_or_none.return_value = user
        session.execute.return_value = mock_result

        result = await repo.get_by_email("user@example.com")

        assert result == user
        session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, session, repo):
        """get_by_email returns None if not found."""
        mock_result = mock.Mock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        result = await repo.get_by_email("notfound@example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_username(self, session, repo):
        """get_by_username queries by username."""
        user = User(
            id=uuid4(),
            email="user@example.com",
            username="testuser",
            password_hash="hash",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_result = mock.Mock()
        mock_result.scalar_one_or_none.return_value = user
        session.execute.return_value = mock_result

        result = await repo.get_by_username("testuser")

        assert result == user
        session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_username_not_found(self, session, repo):
        """get_by_username returns None if not found."""
        mock_result = mock.Mock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        result = await repo.get_by_username("notexist")

        assert result is None

    @pytest.mark.asyncio
    async def test_create(self, session, repo):
        """create adds user to session."""
        result = await repo.create(
            email="new@example.com",
            username="newuser",
            password_hash="hashed",
        )

        session.add.assert_called_once()
        session.flush.assert_called_once()
        assert result.email == "new@example.com"
        assert result.username == "newuser"
        assert result.password_hash == "hashed"


class TestRefreshTokenRepository:
    """Tests for RefreshTokenRepository methods."""

    @pytest.fixture
    def session(self):
        """Mock AsyncSession."""
        return mock.AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, session):
        """RefreshTokenRepository instance."""
        return RefreshTokenRepository(session)

    @pytest.mark.asyncio
    async def test_create(self, session, repo):
        """create adds refresh token to session."""
        user_id = uuid4()
        token_id = uuid4()
        expires_at = datetime.now(UTC)

        result = await repo.create(
            user_id=user_id,
            token_id=token_id,
            token_hash="hash123",
            expires_at=expires_at,
        )

        session.add.assert_called_once()
        session.flush.assert_called_once()
        assert result.user_id == user_id
        assert result.token_id == token_id
        assert result.token_hash == "hash123"

    @pytest.mark.asyncio
    async def test_get_by_token_hash(self, session, repo):
        """get_by_token_hash queries by token hash."""
        token = RefreshToken(
            id=uuid4(),
            user_id=uuid4(),
            token_id=uuid4(),
            token_hash="hash123",
            expires_at=datetime.now(UTC),
        )
        mock_result = mock.Mock()
        mock_result.scalar_one_or_none.return_value = token
        session.execute.return_value = mock_result

        result = await repo.get_by_token_hash("hash123")

        assert result == token
        session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_token_hash_not_found(self, session, repo):
        """get_by_token_hash returns None if not found."""
        mock_result = mock.Mock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        result = await repo.get_by_token_hash("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_revoke(self, session, repo):
        """revoke sets revoked_at on token."""
        token = RefreshToken(
            id=uuid4(),
            user_id=uuid4(),
            token_id=uuid4(),
            token_hash="hash123",
            expires_at=datetime.now(UTC),
            revoked_at=None,
        )
        revoked_at = datetime.now(UTC)

        await repo.revoke(token, revoked_at)

        assert token.revoked_at == revoked_at
        session.flush.assert_called_once()
