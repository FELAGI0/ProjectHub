"""Business logic for user accounts and authentication."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import (
    AuthenticationRequiredError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.modules.users.models import User
from app.modules.users.repository import RefreshTokenRepository, UserRepository
from app.modules.users.schemas import (
    AuthenticationResponse,
    TokenPairResponse,
    UserLoginRequest,
    UserRegistrationRequest,
    UserResponse,
)


class UserService:
    """Coordinates users, credentials, and refresh-token persistence."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._users = UserRepository(session)
        self._refresh_tokens = RefreshTokenRepository(session)

    async def register(
        self, payload: UserRegistrationRequest
    ) -> AuthenticationResponse:
        """Register a user and issue its first token pair."""

        email = str(payload.email).lower()
        username = payload.username.lower()
        if await self._users.get_by_email(email):
            raise UserAlreadyExistsError("Email address is already registered.")
        if await self._users.get_by_username(username):
            raise UserAlreadyExistsError("Username is already registered.")

        user = await self._users.create(
            email=email,
            username=username,
            password_hash=hash_password(payload.password),
        )
        response = await self._build_authentication_response(user)
        await self._session.commit()
        return response

    async def login(self, payload: UserLoginRequest) -> AuthenticationResponse:
        """Authenticate a user and issue a new token pair."""

        user = await self._users.get_by_email(str(payload.email).lower())
        if user is None or not user.is_active:
            raise InvalidCredentialsError()
        if not verify_password(payload.password, user.password_hash):
            raise InvalidCredentialsError()

        response = await self._build_authentication_response(user)
        await self._session.commit()
        return response

    async def refresh(self, token: str) -> AuthenticationResponse:
        """Rotate a valid refresh token and issue a new token pair."""

        payload = decode_token(token, self._settings, expected_type="refresh")
        user_id = self._get_user_id(payload)
        token_id = self._get_token_id(payload)
        persisted_token = await self._refresh_tokens.get_by_token_hash(
            hash_token(token)
        )
        now = datetime.now(UTC)
        if (
            persisted_token is None
            or persisted_token.token_id != token_id
            or persisted_token.revoked_at is not None
            or persisted_token.expires_at <= now
        ):
            raise AuthenticationRequiredError("Invalid or expired refresh token.")

        user = await self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationRequiredError("User account is unavailable.")

        await self._refresh_tokens.revoke(persisted_token, revoked_at=now)
        response = await self._build_authentication_response(user)
        await self._session.commit()
        return response

    async def get_current_user(self, token: str) -> User:
        """Resolve an active user from a valid access token."""

        payload = decode_token(token, self._settings, expected_type="access")
        user = await self._users.get_by_id(self._get_user_id(payload))
        if user is None:
            raise UserNotFoundError()
        if not user.is_active:
            raise AuthenticationRequiredError("User account is inactive.")
        return user

    async def _build_authentication_response(
        self, user: User
    ) -> AuthenticationResponse:
        """Create and persist a new token pair for a user."""

        access_token, expires_in = create_access_token(user.id, self._settings)
        refresh_token, token_id, refresh_expires_at = create_refresh_token(
            user.id, self._settings
        )
        await self._refresh_tokens.create(
            user_id=user.id,
            token_id=token_id,
            token_hash=hash_token(refresh_token),
            expires_at=refresh_expires_at,
        )
        return AuthenticationResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenPairResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                access_token_expires_in=expires_in,
            ),
        )

    @staticmethod
    def _get_user_id(payload: dict[str, object]) -> UUID:
        """Extract a valid UUID user subject from a decoded JWT payload."""

        try:
            return UUID(str(payload["sub"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise AuthenticationRequiredError("Invalid token subject.") from exc

    @staticmethod
    def _get_token_id(payload: dict[str, object]) -> UUID:
        """Extract a valid refresh-token identifier from a decoded JWT payload."""

        try:
            return UUID(str(payload["jti"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise AuthenticationRequiredError("Invalid refresh token.") from exc
