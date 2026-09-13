"""Request and response schemas for users and authentication."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

Username = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_lower=True,
        min_length=3,
        max_length=50,
        pattern=r"^[a-z0-9][a-z0-9_-]*$",
    ),
]
Password = Annotated[str, StringConstraints(min_length=12, max_length=128)]


class UserRegistrationRequest(BaseModel):
    """Payload for creating a user account."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    username: Username
    password: Password


class UserLoginRequest(BaseModel):
    """Payload for exchanging credentials for tokens."""

    email: EmailStr
    password: Password


class RefreshTokenRequest(BaseModel):
    """Payload for rotating a refresh token."""

    refresh_token: str = Field(min_length=1)


class UserResponse(BaseModel):
    """Public representation of a user account."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenPairResponse(BaseModel):
    """Access and refresh tokens issued for an authenticated user."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_token_expires_in: int


class UserUpdateRequest(BaseModel):
    """Payload for updating user profile information."""

    model_config = ConfigDict(str_strip_whitespace=True)

    username: Username | None = None
    email: EmailStr | None = None


class AuthenticationResponse(BaseModel):
    """Authenticated user details together with an issued token pair."""

    user: UserResponse
    tokens: TokenPairResponse
