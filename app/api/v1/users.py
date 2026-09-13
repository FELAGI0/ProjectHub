"""User API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.core.config import get_settings
from app.db.session import get_db_session
from app.modules.users.schemas import UserResponse, UserUpdateRequest
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserService:
    """Create a users service bound to the current request session."""

    return UserService(session, get_settings())


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current user",
)
async def get_me(current_user: CurrentUser) -> UserResponse:
    """Return the authenticated user's public profile."""

    return UserResponse.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update the current user",
    status_code=status.HTTP_200_OK,
)
async def update_me(
    payload: UserUpdateRequest,
    current_user: CurrentUser,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Update the authenticated user's profile information."""

    return await service.update_user(current_user.id, payload)
