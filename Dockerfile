# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.9.22 /uv /uvx /bin/

COPY pyproject.toml README.md ./
RUN uv sync --no-dev --no-install-project

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh && uv sync --no-dev

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
