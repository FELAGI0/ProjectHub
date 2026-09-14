"""Authentication API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.session import get_db_session
from app.modules.users.schemas import (
    AuthenticationResponse,
    LogoutRequest,
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
@limiter.limit("3/minute")
async def register(
    request: Request,
    response: Response,
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
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
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
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    response: Response,
    payload: RefreshTokenRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> AuthenticationResponse:
    """Rotate a valid refresh token and issue a new token pair."""

    return await service.refresh(payload.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout current session",
    description="Revoke the provided refresh token. Idempotent.",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Token revoked, already revoked, or not found."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid or expired refresh token."
        },
    },
)
@limiter.limit("20/minute")
async def logout(
    request: Request,
    response: Response,
    body: LogoutRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    """Revoke a refresh token."""
    await service.logout(body.refresh_token)


@router.post(
    "/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout from all devices",
    description="Revoke all refresh tokens for the current user.",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "All tokens revoked."},
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid access token."
        },
    },
)
@limiter.limit("20/minute")
async def logout_all(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    """Revoke all refresh tokens for the current user."""
    await service.logout_all(current_user.id)
