"""List all users for the global team directory."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User


class UserSummaryResponse(BaseModel):
    """Public user fields exposed in the global team directory."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime


class PaginatedUsersResponse(BaseModel):
    """Paginated list of users."""

    items: list[UserSummaryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserListRepository:
    """Read-only user directory queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_users(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
    ) -> tuple[list[User], int]:
        """Return a paginated, optionally filtered user directory."""

        stmt = select(User)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                User.username.ilike(pattern) | User.email.ilike(pattern)
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._session.execute(count_stmt)).scalar_one()

        stmt = (
            stmt.order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        users = list((await self._session.execute(stmt)).scalars().all())
        return users, total


class UserDirectoryService:
    """Business logic for the authenticated user directory."""

    def __init__(self, session: AsyncSession) -> None:
        self._users = UserListRepository(session)

    async def list_users(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
    ) -> PaginatedUsersResponse:
        """Return a paginated list of all active users."""

        users, total = await self._users.list_users(
            page=page, page_size=page_size, search=search
        )
        total_pages = -(-total // page_size) if total > 0 else 1
        items = [
            UserSummaryResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                is_active=user.is_active,
                created_at=user.created_at,
            )
            for user in users
        ]
        return PaginatedUsersResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )



