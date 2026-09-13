"""Run database migrations."""

import asyncio

from alembic import command
from alembic.config import Config


async def run_migrations():
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")


if __name__ == "__main__":
    asyncio.run(run_migrations())
