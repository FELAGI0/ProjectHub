# Development Setup Guide

This guide provides detailed instructions for setting up a development environment for ProjectHub.

## Prerequisites

- **Python 3.13+**
- **PostgreSQL 16+** (or Docker)
- **Git**
- **[uv](https://github.com/astral-sh/uv)** (recommended) or pip

## Quick Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/projecthub.git
cd projecthub

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env  # or your preferred editor

# Start PostgreSQL (if using Docker)
docker run -d \
  --name projecthub-postgres \
  -e POSTGRES_DB=projecthub \
  -e POSTGRES_USER=projecthub \
  -e POSTGRES_PASSWORD=your-password \
  -p 5432:5432 \
  postgres:16-alpine

# Run migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn app.main:app --reload
```

## Detailed Setup Steps

### 1. Database Setup

#### Option A: Docker (Recommended)

```bash
docker run -d \
  --name projecthub-postgres \
  -e POSTGRES_DB=projecthub \
  -e POSTGRES_USER=projecthub \
  -e POSTGRES_PASSWORD=dev-password \
  -p 5432:5432 \
  postgres:16-alpine
```

#### Option B: Local PostgreSQL

```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE projecthub;
CREATE USER projecthub WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE projecthub TO projecthub;
\q
```

### 2. Environment Configuration

Edit `.env` file:

```bash
# Application
APP_NAME=ProjectHub
DEBUG=true                    # Enable debug mode for development
LOG_LEVEL=DEBUG              # Verbose logging

# Database
POSTGRES_DB=projecthub
POSTGRES_USER=projecthub
POSTGRES_PASSWORD=dev-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Security (generate a secure random key)
JWT_SECRET_KEY=your-development-secret-key-at-least-32-chars
```

### 3. Database Migrations

```bash
# Apply all migrations
uv run alembic upgrade head

# Verify migration status
uv run alembic current

# View migration history
uv run alembic history
```

### 4. Verify Installation

```bash
# Run tests
uv run pytest

# Check code quality
uv run ruff check app tests
uv run mypy app

# Start server
uv run uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs to see the API documentation.

## Development Workflow

### Running the Application

```bash
# Development server with auto-reload
uv run uvicorn app.main:app --reload

# With custom host and port
uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# With debug logging
LOG_LEVEL=DEBUG uv run uvicorn app.main:app --reload
```

### Database Management

```bash
# Create a new migration after model changes
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Rollback to specific revision
uv run alembic downgrade <revision_id>

# Reset database (WARNING: destroys all data)
uv run alembic downgrade base
uv run alembic upgrade head
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/api/test_projects.py

# Run specific test class
uv run pytest tests/api/test_projects.py::TestListProjects

# Run specific test
uv run pytest tests/api/test_projects.py::TestListProjects::test_success

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=app --cov-report=html
# View coverage report at htmlcov/index.html

# Run only failed tests
uv run pytest --lf

# Run tests in parallel (faster)
uv run pytest -n auto
```

### Code Quality

```bash
# Run linter
uv run ruff check app tests

# Auto-fix linting issues
uv run ruff check --fix app tests

# Format code
uv run ruff format app tests

# Type checking
uv run mypy app

# Run all checks
uv run ruff check app && \
uv run ruff format --check app && \
uv run mypy app && \
uv run pytest
```

## IDE Setup

### VS Code

Install extensions:
- Python
- Pylance
- Ruff

Create `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "python.analysis.typeCheckingMode": "basic"
}
```

### PyCharm

1. Mark `app` as Sources Root
2. Enable Python type hints
3. Configure ruff as external tool
4. Set line length to 88

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker ps  # if using Docker
sudo systemctl status postgresql  # Linux

# Test connection
psql -h localhost -U projecthub -d projecthub
```

### Migration Conflicts

```bash
# If migrations are out of sync
uv run alembic stamp head  # Mark current state as head

# If you have conflicts after pulling changes
uv run alembic downgrade base
uv run alembic upgrade head
```

### Module Import Errors

```bash
# Reinstall dependencies
uv sync --reinstall

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name '*.pyc' -delete
```

## Tips and Best Practices

1. **Use feature branches**: `git checkout -b feature/my-feature`
2. **Run tests before committing**: `uv run pytest`
3. **Keep dependencies updated**: `uv sync --upgrade`
4. **Use meaningful commit messages**: Follow conventional commits
5. **Review migrations**: Always check auto-generated migrations
6. **Test migrations up and down**: Ensure they're reversible
7. **Use `.env` for secrets**: Never commit sensitive data
8. **Enable pre-commit hooks**: Run linting/tests automatically

## Pre-commit Hooks (Optional)

Install pre-commit:

```bash
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: uv run pytest
        language: system
        pass_filenames: false
        always_run: true
EOF

# Install hooks
pre-commit install
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)

## Getting Help

- Check [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
- Open an issue on GitHub for bugs or questions
- Review existing issues and PRs for similar problems
