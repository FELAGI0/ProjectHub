#!/bin/sh
set -e

echo "Running database migrations..."
uv run python -m alembic upgrade head

echo "Starting uvicorn server..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
