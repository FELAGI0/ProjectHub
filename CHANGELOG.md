# Changelog

All notable changes to ProjectHub will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-08

### Added
- Initial release of ProjectHub
- User authentication with JWT (access + refresh tokens)
- User registration and login endpoints
- Project management (CRUD operations)
- Task management with status and priority
- Project member management with role-based access control
- Three-tier role system (MEMBER, ADMIN, OWNER)
- RESTful API with FastAPI
- PostgreSQL database integration with async SQLAlchemy
- Alembic database migrations
- Comprehensive test suite (132+ tests)
- Docker and Docker Compose support
- API documentation with Swagger/ReDoc
- Health check endpoint
- JSON structured logging
- Type hints and Pydantic validation throughout
- Password hashing with Argon2
- Environment-based configuration
- Professional documentation (README, CONTRIBUTING, SECURITY)

### Security
- JWT-based authentication with token rotation
- Argon2 password hashing
- Role-based authorization checks
- Input validation on all endpoints
- SQL injection protection via ORM
- Secure password requirements

---

[Unreleased]: https://github.com/yourusername/projecthub/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/projecthub/releases/tag/v0.1.0
