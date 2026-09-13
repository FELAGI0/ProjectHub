"""Persistence operations for the users module."""

from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID

from sqlalchemy import CursorResult, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import RefreshToken, User


class UserRepository:
    """Database access methods for user accounts."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Return a user by its identifier."""

        return await self._session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        """Return a user by normalized email address."""

        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Return a user by normalized username."""

        result = await self._session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create(self, *, email: str, username: str, password_hash: str) -> User:
        """Add a new user to the current transaction."""

        user = User(email=email, username=username, password_hash=password_hash)
        self._session.add(user)
        await self._session.flush()
        return user

    async def update(
        self,
        user: User,
        *,
        email: str | None = None,
        username: str | None = None,
    ) -> User:
        """Update user profile information in the current transaction."""

        if email is not None:
            user.email = email
        if username is not None:
            user.username = username
        await self._session.flush()
        return user


class RefreshTokenRepository:
    """Database access methods for refresh-token lifecycle management."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: UUID,
        token_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """Persist a new refresh token in the current transaction."""

        refresh_token = RefreshToken(
            user_id=user_id,
            token_id=token_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self._session.add(refresh_token)
        await self._session.flush()
        return refresh_token

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """Return a refresh token by its non-reversible digest."""

        result = await self._session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def revoke(self, refresh_token: RefreshToken, revoked_at: datetime) -> None:
        """Mark a refresh token as revoked in the current transaction."""

        refresh_token.revoked_at = revoked_at
        await self._session.flush()

    async def revoke_by_token_id(self, token_id: UUID) -> bool:
        """Mark token as revoked by its jti. Returns True if updated."""

        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token_id == token_id)
            .where(RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )
        result = await self._session.execute(stmt)
        return cast(CursorResult[Any], result).rowcount > 0

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """Revoke all active tokens for a user. Returns count."""

        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )
        result = await self._session.execute(stmt)
        return cast(CursorResult[Any], result).rowcount
