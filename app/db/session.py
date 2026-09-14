"""Async SQLAlchemy engine and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from app.core.config import Settings, get_settings


def create_database_url(settings: Settings) -> URL:
    """Build a safe SQLAlchemy URL for the PostgreSQL async driver."""

    if settings.database_url is not None:
        database_url = make_url(settings.database_url)
        return database_url.set(drivername="postgresql+asyncpg")

    return URL.create(
        drivername="postgresql+asyncpg",
        username=settings.postgres_user,
        password=settings.postgres_password,
        host=settings.postgres_host,
        port=settings.postgres_port,
        database=settings.postgres_db,
    )


def create_database_engine(settings: Settings) -> AsyncEngine:
    """Create the application asynchronous database engine."""

    return create_async_engine(
        create_database_url(settings),
        connect_args={"ssl": settings.postgres_ssl},
        pool_pre_ping=True,
    )


settings = get_settings()
engine = create_database_engine(settings)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Yield a database session and close it after request processing."""

    async with async_session_factory() as session:
        yield session


async def close_database_engine() -> None:
    """Dispose the application engine and close all pooled connections."""

    await engine.dispose()
