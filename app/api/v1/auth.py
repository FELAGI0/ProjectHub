"""Authentication API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db_session
from app.modules.users.schemas import (
    AuthenticationResponse,
    RefreshTokenRequest,
    UserLoginRequest,
    UserRegistrationRequest,
)
from app.modules.users.service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserService:
    """Create a users service bound to the current request session."""

    return UserService(session, get_settings())


@router.post(
    "/register",
    response_model=AuthenticationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user account",
)
async def register(
    payload: UserRegistrationRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> AuthenticationResponse:
    """Register a user and return its first access and refresh tokens."""

    return await service.register(payload)


@router.post(
    "/login",
    response_model=AuthenticationResponse,
    summary="Authenticate a user",
)
async def login(
    payload: UserLoginRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> AuthenticationResponse:
    """Authenticate a user and issue an access and refresh token pair."""

    return await service.login(payload)


@router.post(
    "/refresh",
    response_model=AuthenticationResponse,
    summary="Rotate a refresh token",
)
async def refresh(
    payload: RefreshTokenRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> AuthenticationResponse:
    """Rotate a valid refresh token and issue a new token pair."""

    return await service.refresh(payload.refresh_token)
