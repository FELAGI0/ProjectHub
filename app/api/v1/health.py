"""Health check endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    """Response returned when the application is available."""

    status: str


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check application availability",
    description="Returns a successful response when the API process is running.",
)
async def get_health() -> HealthResponse:
    """Return the current application health state."""

    return HealthResponse(status="ok")
