"""Integration tests for PostgreSQL connectivity."""

import os

import pytest
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import create_database_engine


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.getenv("CI") != "true",
    reason="Requires PostgreSQL instance (run in CI environment)",
)
async def test_database_connection_executes_select_one() -> None:
    """The configured PostgreSQL instance accepts a query from an async engine."""

    engine = create_database_engine(get_settings())

    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))

        assert result.scalar_one() == 1
    finally:
        await engine.dispose()

    assert engine.pool.checkedout() == 0
