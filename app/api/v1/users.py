"""User API endpoints."""

from fastapi import APIRouter

from app.api.dependencies.auth import CurrentUser
from app.modules.users.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current user",
)
async def get_me(current_user: CurrentUser) -> UserResponse:
    """Return the authenticated user's public profile."""

    return UserResponse.model_validate(current_user)
