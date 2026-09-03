"""Authentication dependencies for protected API endpoints."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AuthenticationRequiredError
from app.db.session import get_db_session
from app.modules.users.models import User
from app.modules.users.service import UserService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    """Return the active user represented by a Bearer access token."""

    if credentials is None:
        raise AuthenticationRequiredError()

    return await UserService(session, get_settings()).get_current_user(
        credentials.credentials
    )


CurrentUser = Annotated[User, Depends(get_current_user)]
