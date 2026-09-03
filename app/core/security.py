"""Password hashing and JSON Web Token primitives."""

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import UUID, uuid4

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import Settings
from app.core.exceptions import AuthenticationRequiredError

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plaintext password using pwdlib's recommended Argon2 settings."""

    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against its stored Argon2 hash."""

    return password_hasher.verify(password, password_hash)


def hash_token(token: str) -> str:
    """Return a non-reversible digest suitable for refresh-token persistence."""

    return sha256(token.encode("utf-8")).hexdigest()


def create_access_token(user_id: UUID, settings: Settings) -> tuple[str, int]:
    """Create a short-lived signed access token and return its lifetime in seconds."""

    expires_in = settings.jwt_access_token_expire_minutes * 60
    return _create_token(
        user_id=user_id,
        token_type="access",
        expires_delta=timedelta(seconds=expires_in),
        settings=settings,
    ), expires_in


def create_refresh_token(
    user_id: UUID, settings: Settings
) -> tuple[str, UUID, datetime]:
    """Create a signed refresh token with a unique identifier and expiry date."""

    expires_at = datetime.now(UTC) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    token_id = uuid4()
    return (
        _create_token(
            user_id=user_id,
            token_type="refresh",
            expires_delta=timedelta(days=settings.jwt_refresh_token_expire_days),
            settings=settings,
            token_id=token_id,
        ),
        token_id,
        expires_at,
    )


def decode_token(
    token: str, settings: Settings, expected_type: str
) -> dict[str, object]:
    """Decode a token and validate that it is the expected token type."""

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
    except (ExpiredSignatureError, InvalidTokenError) as exc:
        raise AuthenticationRequiredError("Invalid or expired token.") from exc

    if payload.get("type") != expected_type:
        raise AuthenticationRequiredError("Invalid token type.")

    return payload


def _create_token(
    *,
    user_id: UUID,
    token_type: str,
    expires_delta: timedelta,
    settings: Settings,
    token_id: UUID | None = None,
) -> str:
    """Build and sign a JWT payload."""

    issued_at = datetime.now(UTC)
    payload: dict[str, object] = {
        "sub": str(user_id),
        "type": token_type,
        "iat": issued_at,
        "exp": issued_at + expires_delta,
    }
    if token_id is not None:
        payload["jti"] = str(token_id)

    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
