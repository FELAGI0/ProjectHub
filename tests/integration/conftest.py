"""Integration-test fixtures backed by a disposable PostgreSQL container."""

from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.community.postgres import PostgresContainer

from app.core.config import Settings
from app.db.session import create_database_url, get_db_session


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Mark all tests under the integration directory."""
    for item in items:
        if "/integration/" in item.fspath.strpath.replace("\\", "/"):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    """Start a disposable PostgreSQL container for integration tests."""
    try:
        with PostgresContainer("postgres:16-alpine") as container:
            yield container
    except Exception as exc:
        pytest.skip(f"Docker unavailable: {exc}")


@pytest.fixture(scope="session")
def test_settings(postgres_container: PostgresContainer) -> Settings:
    """Build application settings for the disposable PostgreSQL container."""
    return Settings(
        postgres_host=postgres_container.get_container_host_ip(),
        postgres_port=int(postgres_container.get_exposed_port(5432)),
        postgres_db=postgres_container.dbname,
        postgres_user=postgres_container.username,
        postgres_password=postgres_container.password,
        jwt_secret_key="test-secret-key-for-integration-at-least-32-chars",
        cors_origins=["http://test"],
        log_level="WARNING",
    )


@pytest.fixture(scope="session")
def database_url(test_settings: Settings) -> str:
    """Return the async database URL for the PostgreSQL test container."""
    return create_database_url(test_settings).render_as_string(hide_password=False)


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(
    postgres_container: PostgresContainer,
    database_url: str,
) -> Iterator[None]:
    """Apply all Alembic migrations to the PostgreSQL test container."""
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")
    yield


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine(database_url: str) -> AsyncIterator[AsyncEngine]:
    """Create an async engine without connection reuse between tests."""
    engine = create_async_engine(database_url, poolclass=NullPool)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def db_session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Yield a session whose committed changes roll back after each test."""
    connection = await engine.connect()
    outer_transaction = await connection.begin()
    session = AsyncSession(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        await session.close()
        await outer_transaction.rollback()
        await connection.close()


@pytest.fixture
def app(test_settings: Settings, db_session: AsyncSession):
    """Create an application bound to the isolated test database session."""
    from app.factory import create_application

    application = create_application(settings=test_settings)

    async def override_get_db_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    application.dependency_overrides[get_db_session] = override_get_db_session
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    """Yield an HTTP client connected to the isolated application instance."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_client:
        yield async_client
