"""User API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.core.config import get_settings
from app.db.session import get_db_session
from app.modules.users.directory import (
    PaginatedUsersResponse,
    UserDirectoryService,
)
from app.modules.users.schemas import UserResponse, UserUpdateRequest
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserService:
    """Create a users service bound to the current request session."""

    return UserService(session, get_settings())


def get_user_directory_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserDirectoryService:
    """Create a user directory service bound to the request session."""

    return UserDirectoryService(session)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current user",
)
async def get_me(current_user: CurrentUser) -> UserResponse:
    """Return the authenticated user's public profile."""

    return UserResponse.model_validate(current_user)


@router.get(
    "/",
    response_model=PaginatedUsersResponse,
    summary="List users",
    description=(
        "Return a paginated directory of all registered users. Supports search"
        " by username or email."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid authentication token."
        },
    },
)
async def list_users(
    current_user: CurrentUser,
    service: Annotated[UserDirectoryService, Depends(get_user_directory_service)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=100),
) -> PaginatedUsersResponse:
    """List all registered users."""

    return await service.list_users(
        page=page, page_size=page_size, search=search
    )


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
