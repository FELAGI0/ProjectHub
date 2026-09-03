# ProjectHub

ProjectHub is a backend platform for managing projects and teams, inspired by
Jira, Trello, and GitHub Issues. The project is being developed as a portfolio
application with production-oriented engineering practices.

## Technology stack

- Python 3.13+
- FastAPI and Pydantic v2
- Pydantic Settings for application configuration
- PostgreSQL 16 in Docker Compose
- SQLAlchemy 2.0 async with asyncpg
- Alembic migrations
- Pytest, Ruff, and MyPy
- Docker Compose

## Implemented

- Base modular application structure.
- FastAPI application factory.
- Versioned public API under `/api/v1`.
- Configured OpenAPI, Swagger UI, and ReDoc under the API prefix.
- Environment-based settings implemented with `pydantic-settings`.
- Standard-library logging configuration.
- Health check endpoint and its API test.
- Docker Compose configuration for API and PostgreSQL.
- PostgreSQL settings, async SQLAlchemy engine, and session factory.
- Integration test for `SELECT 1` with guaranteed engine disposal.
- Async Alembic configuration and an initial migration baseline.

## Run locally

1. Install [uv](https://docs.astral.sh/uv/).
2. Create the local environment file:

   ```bash
   cp .env.example .env
   ```

   On PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

3. Install dependencies:

   ```bash
   uv sync --all-groups
   ```

4. Start the API:

   ```bash
   uv run uvicorn app.main:app --reload
   ```

## Run with Docker Compose

```bash
docker compose up --build
```

Use `docker compose down` to stop containers. Do not use `docker compose down -v`
unless local PostgreSQL data may be discarded.

## Available endpoints

- `GET /api/v1/health` — application availability check.
- `GET /api/v1/docs` — Swagger UI.
- `GET /api/v1/redoc` — ReDoc.
- `GET /api/v1/openapi.json` — OpenAPI specification.

## Quality checks

```bash
uv run ruff check .
uv run mypy
uv run pytest
```

## Database migrations

```bash
docker compose up -d postgres
uv run alembic upgrade head
uv run alembic current
```

## Next steps

- Implement the `User` model and basic JWT authentication.
- Add projects, memberships, tasks, labels, and comments.
