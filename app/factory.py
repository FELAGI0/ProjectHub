"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as api_v1_router
from app.core.config import get_settings
from app.core.exceptions import DomainError
from app.core.logging import configure_logging
from app.db.session import close_database_engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Release database resources when the application shuts down."""

    yield
    await close_database_engine()


async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
    """Convert known domain errors into a consistent API response."""

    headers: dict[str, str] = {}
    if exc.status_code == 401:
        headers["WWW-Authenticate"] = "Bearer"
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers,
    )


def create_application() -> FastAPI:
    """Create and configure the ProjectHub FastAPI application."""

    settings = get_settings()
    configure_logging(settings)
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="API for project and team management.",
        debug=settings.debug,
        lifespan=lifespan,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
    )

    # CORS middleware configuration
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_exception_handler(DomainError, domain_error_handler)
    application.include_router(api_v1_router, prefix=settings.api_v1_prefix)
    return application
