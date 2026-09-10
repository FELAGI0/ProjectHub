# Contributing to ProjectHub

Thank you for considering contributing to ProjectHub! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions. We are committed to providing a welcoming environment for everyone.

## How to Contribute

### Reporting Bugs

Before creating a bug report:
- Check if the issue already exists in GitHub Issues
- Verify you're using the latest version
- Collect relevant information (error messages, logs, environment details)

When reporting:
- Use a clear, descriptive title
- Describe the exact steps to reproduce
- Provide actual vs expected behavior
- Include error messages and stack traces
- Mention your environment (OS, Python version, etc.)

### Suggesting Features

Feature requests are welcome! Please:
- Use a clear, descriptive title
- Explain the problem this feature would solve
- Describe the proposed solution
- Consider alternative solutions
- Explain why this benefits the project

### Pull Requests

#### Before Starting

1. Check existing issues and PRs to avoid duplicates
2. Open an issue to discuss significant changes
3. Fork the repository and create a feature branch

#### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/projecthub.git
cd projecthub

# Install dependencies
uv sync

# Create a feature branch
git checkout -b feature/your-feature-name
```

#### Making Changes

**Code Style:**
- Follow PEP 8 (enforced by ruff)
- Use type hints for all functions
- Keep line length to 88 characters
- Write docstrings for public functions/classes

**Architecture:**
- Maintain the three-layer architecture (API → Service → Repository)
- Don't bypass layers (e.g., API calling Repository directly)
- Use dependency injection
- Raise domain exceptions, don't return error codes

**Testing:**
- Add tests for all new features
- Update tests when modifying existing features
- Aim for high coverage on critical paths
- Include both unit and API tests

**Commits:**
- Write clear, descriptive commit messages
- Keep commits atomic (one logical change per commit)
- Use present tense ("Add feature" not "Added feature")
- Reference issue numbers when applicable

#### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/api/test_projects.py

# Run with coverage
uv run pytest --cov=app --cov-report=html
```

#### Code Quality Checks

```bash
# Linting
uv run ruff check app tests

# Type checking
uv run mypy app

# Auto-fix linting issues
uv run ruff check --fix app tests
```

#### Submitting Your PR

1. Ensure all tests pass
2. Ensure linting and type checking pass
3. Update documentation if needed
4. Commit your changes with clear messages
5. Push to your fork
6. Open a Pull Request

**PR Description Should Include:**
- What changes were made
- Why the changes were necessary
- How to test the changes
- Any breaking changes
- Related issue numbers

#### PR Review Process

1. Automated checks will run (tests, linting, type checking)
2. Maintainers will review your code
3. Address any requested changes
4. Once approved, your PR will be merged

## Development Guidelines

### Project Structure

```
app/
├── api/           # API layer - FastAPI routers
├── core/          # Core utilities (config, security, logging)
├── db/            # Database configuration
└── modules/       # Domain modules
    └── <module>/
        ├── models.py      # SQLAlchemy models
        ├── repository.py  # Data access layer
        ├── schemas.py     # Pydantic schemas
        └── service.py     # Business logic
```

### Adding a New Module

1. Create module directory in `app/modules/<module_name>/`
2. Add the four core files: `models.py`, `repository.py`, `schemas.py`, `service.py`
3. Create migration: `uv run alembic revision --autogenerate -m "Add <module>"`
4. Create API router in `app/api/v1/<module_name>.py`
5. Register router in `app/api/v1/router.py`
6. Add tests in `tests/api/` and `tests/unit/`

### Database Migrations

- Always use Alembic for schema changes
- Never use `create_all()` or raw SQL outside migrations
- Test migrations up and down
- Review auto-generated migrations carefully

### Security Best Practices

- Never commit secrets or credentials
- Use environment variables for configuration
- Validate all user input with Pydantic
- Use parameterized queries (SQLAlchemy does this)
- Hash passwords with Argon2 (via pwdlib)
- Implement proper authorization checks

### Testing Best Practices

- Mock external dependencies
- Test both success and failure paths
- Test edge cases and validation
- Use descriptive test names
- Keep tests independent and isolated

## Questions?

Feel free to open an issue for questions or clarifications.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
