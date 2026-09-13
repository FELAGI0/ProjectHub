"""Health check endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session

router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    """Response returned when the application is available."""

    status: str
    database: str


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check application availability",
    description="Returns the application and database health state.",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Database is unavailable."
        }
    },
)
async def get_health(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> HealthResponse:
    """Return the current application health state."""

    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(status="degraded", database="unavailable")
    return HealthResponse(status="ok", database="ok")
