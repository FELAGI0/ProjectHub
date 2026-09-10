# ProjectHub

**ProjectHub** is a modern, full-stack project management application. Built with FastAPI (backend) and React 19 (frontend), it provides a complete solution for managing projects, tasks, and team collaboration with role-based access control.

![Python Version](https://img.shields.io/badge/python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)
![React](https://img.shields.io/badge/React-19-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

### Backend
- **User Management**: Registration, authentication with JWT tokens (access + refresh)
- **Project Management**: Create, update, delete projects with ownership tracking
- **Task Management**: Full CRUD operations with status, priority, and filtering
- **Team Collaboration**: Role-based access control (MEMBER, ADMIN, OWNER)
- **Member Management**: Add/remove team members, manage roles and permissions
- **RESTful API**: Clean, documented API following REST principles
- **Type Safety**: Full type hints coverage with Pydantic validation
- **Database Migrations**: Alembic integration for schema versioning
- **Comprehensive Testing**: 132+ tests covering all endpoints and business logic

### Frontend
- **Modern UI**: Responsive interface with dark mode support
- **Kanban Board**: Drag-and-drop task management with @dnd-kit
- **Real-time Updates**: Optimistic UI updates with TanStack Query v5
- **Form Validation**: React Hook Form + Zod for type-safe forms
- **Toast Notifications**: User feedback with Sonner
- **Error Handling**: Global error boundary and 404 page
- **Accessibility**: WCAG-compliant components with proper ARIA attributes
- **Type Safety**: Full TypeScript coverage with strict mode

## 🏗️ Architecture

### Backend Architecture

Three-layer architecture following separation of concerns:

```
┌─────────────────────────────────────────┐
│             API Layer                   │  ← FastAPI routers & endpoints
│  (app/api/v1/*.py)                      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          Service Layer                  │  ← Business logic & authorization
│  (app/modules/*/service.py)             │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Repository Layer                 │  ← Data access & persistence
│  (app/modules/*/repository.py)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          PostgreSQL                     │  ← Database
└─────────────────────────────────────────┘
```

### Frontend Architecture

Feature-Sliced Design with clear separation between layers:

```
frontend/src/
├── app/                    # Application layer
│   ├── providers/          # Context providers (Query, Theme)
│   └── router/             # Route configuration
├── pages/                  # Page components
├── widgets/                # Complex UI blocks (Layout)
├── features/               # Business features
│   ├── auth/               # Authentication feature
│   ├── projects/           # Projects feature
│   ├── tasks/              # Tasks feature
│   └── project-members/    # Team management feature
└── shared/                 # Shared utilities
    ├── ui/                 # UI components (shadcn/ui)
    ├── api/                # API client configuration
    └── lib/                # Utility functions
```

## 🛠️ Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** 0.115+ - Modern async web framework
- **[Python](https://www.python.org/)** 3.13 - Programming language
- **[PostgreSQL](https://www.postgresql.org/)** 16 - Primary database
- **[SQLAlchemy](https://www.sqlalchemy.org/)** 2.0 - Async ORM
- **[Pydantic](https://docs.pydantic.dev/)** 2.0+ - Data validation
- **[Alembic](https://alembic.sqlalchemy.org/)** - Database migrations
- **[PyJWT](https://pyjwt.readthedocs.io/)** - JWT authentication
- **[pwdlib](https://github.com/frankie567/pwdlib)** - Password hashing (Argon2)

### Frontend
- **[React](https://react.dev/)** 19 - UI library
- **[TypeScript](https://www.typescriptlang.org/)** 5.7 - Type safety
- **[Vite](https://vite.dev/)** 7 - Build tool
- **[TanStack Query](https://tanstack.com/query)** 5 - Server state management
- **[React Hook Form](https://react-hook-form.com/)** 7 - Form management
- **[Zod](https://zod.dev/)** - Schema validation
- **[Zustand](https://zustand-demo.pmnd.rs/)** - Client state (auth)
- **[Axios](https://axios-http.com/)** - HTTP client
- **[@dnd-kit](https://dndkit.com/)** - Drag and drop
- **[TailwindCSS](https://tailwindcss.com/)** 4 - Styling
- **[shadcn/ui](https://ui.shadcn.com/)** - UI components
- **[Sonner](https://sonner.emilkowal.ski/)** - Toast notifications
- **[Lucide React](https://lucide.dev/)** - Icons

## 📁 Project Structure

```
projecthub/
├── backend/
│   ├── alembic/                # Database migrations
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies/   # FastAPI dependencies
│   │   │   └── v1/             # API v1 endpoints
│   │   │       ├── auth.py
│   │   │       ├── projects.py
│   │   │       ├── tasks.py
│   │   │       ├── project_members.py
│   │   │       └── users.py
│   │   ├── core/
│   │   │   ├── config.py       # Settings
│   │   │   ├── exceptions.py   # Domain exceptions
│   │   │   └── security.py     # JWT & password utilities
│   │   ├── modules/
│   │   │   ├── users/          # User domain
│   │   │   ├── projects/       # Project domain
│   │   │   ├── tasks/          # Task domain
│   │   │   └── project_members/# Member domain
│   │   └── main.py
│   ├── tests/                  # Backend tests
│   ├── .env.example
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/                # Application layer
│   │   │   ├── providers/      # React Query, Theme, Error Boundary
│   │   │   └── router/         # Routes + guards
│   │   ├── pages/              # Page components
│   │   ├── widgets/            # Layout components
│   │   ├── features/           # Business features
│   │   │   ├── auth/
│   │   │   │   ├── api/        # Auth API client
│   │   │   │   ├── hooks/      # useLogin, useRegister
│   │   │   │   ├── store/      # Zustand auth store
│   │   │   │   └── types/      # TypeScript types
│   │   │   ├── projects/
│   │   │   ├── tasks/
│   │   │   └── project-members/
│   │   └── shared/
│   │       ├── ui/             # shadcn/ui components
│   │       ├── api/            # Axios configuration
│   │       └── lib/            # Utilities
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── compose.yaml                # Docker Compose
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 20+ (for frontend)
- **Python** 3.13+ (for backend)
- **PostgreSQL** 16+ (or use Docker Compose)
- **pnpm/npm** (for frontend dependencies)
- **uv** (recommended for backend) or pip

### Installation

#### 1. Clone the repository
```bash
git clone https://github.com/FELAGI0/projecthub.git
cd projecthub
```

#### 2. Backend Setup

```bash
cd backend

# Set up environment variables
cp .env.example .env
# Edit .env and set your database credentials and JWT secret

# Install dependencies
uv sync

# Run database migrations
uv run alembic upgrade head

# Start the development server
uv run uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Using Docker Compose

The easiest way to run the entire stack:

```bash
# Start all services (API + PostgreSQL + Frontend)
docker compose up -d

# Run migrations
docker compose exec api uv run alembic upgrade head

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📚 API Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout (revoke refresh token)

#### Projects
- `GET /api/v1/projects` - List user's projects
- `POST /api/v1/projects` - Create new project
- `GET /api/v1/projects/{id}` - Get project details
- `PATCH /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

#### Tasks
- `GET /api/v1/projects/{id}/tasks` - List project tasks
- `POST /api/v1/projects/{id}/tasks` - Create task
- `GET /api/v1/tasks/{id}` - Get task details
- `PATCH /api/v1/tasks/{id}` - Update task (status, priority, etc.)
- `DELETE /api/v1/tasks/{id}` - Delete task

#### Project Members
- `GET /api/v1/projects/{id}/members` - List members
- `POST /api/v1/projects/{id}/members` - Add member
- `PATCH /api/v1/projects/{id}/members/{user_id}` - Update member role
- `DELETE /api/v1/projects/{id}/members/{user_id}` - Remove member

## 🔐 Authentication & Authorization

### JWT Authentication
Two-token strategy for secure authentication:
- **Access Token**: Short-lived (15 min), used for API requests
- **Refresh Token**: Long-lived (7 days), used to obtain new access tokens

The frontend automatically handles token refresh and stores tokens securely in localStorage (Zustand persist).

### Role-Based Access Control

| Role | Permissions |
|------|-------------|
| **MEMBER** | View projects, tasks, and members |
| **ADMIN** | + Create/update tasks, add/remove members |
| **OWNER** | + Update/delete project, change member roles |

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/api/test_projects.py
```

**Test Results**: 132+ automated tests
- 69 API integration tests
- 63 Unit tests
- Full coverage of business logic

### Frontend Tests

```bash
cd frontend

# Run tests (when configured)
npm run test

# Type checking
npm run type-check

# Linting
npm run lint
```

## 🔧 Development

### Backend

```bash
# Run linter
uv run ruff check app tests

# Auto-fix issues
uv run ruff check --fix app tests

# Type checking
uv run mypy app

# Run all checks
uv run ruff check app && uv run mypy app && uv run pytest
```

### Frontend

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

## 🌍 Environment Variables

### Backend (.env)
```bash
# Application
APP_NAME=ProjectHub
DEBUG=false
LOG_LEVEL=INFO

# Database
POSTGRES_DB=projecthub
POSTGRES_USER=projecthub
POSTGRES_PASSWORD=your-secure-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Security
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

⚠️ **Security Note**: Never commit `.env` files. Use strong, unique values in production.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For questions or issues, please open an issue on GitHub.

---

Made with ❤️ using Python, TypeScript, FastAPI, and React
