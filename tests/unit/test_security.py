"""Unit tests for security primitives (password hashing, JWT, token hashing)."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from app.core.config import get_settings
from app.core.exceptions import AuthenticationRequiredError
from app.core.security import (
    _create_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)

settings = get_settings()
SECRET = settings.jwt_secret_key.get_secret_value()
ALGORITHM = settings.jwt_algorithm


class TestPasswordHashing:
    """hash_password / verify_password correctness."""

    def test_hash_password_returns_argon2_hash(self) -> None:
        """The hash starts with the Argon2id prefix."""
        hashed = hash_password("correct-horse-battery-staple-1234")
        assert hashed.startswith("$argon2id$"), (
            f"Expected Argon2id prefix, got {hashed!r}"
        )

    def test_verify_password_success(self) -> None:
        """verify_password returns True for the original password."""
        password = "my-secure-password-here-42"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_wrong_password(self) -> None:
        """verify_password returns False for a different password."""
        hashed = hash_password("correct-password-12345678")
        assert verify_password("wrong-password-87654321", hashed) is False


class TestAccessToken:
    """create_access_token / decode_token for 'access' type tokens."""

    def test_create_and_decode_access_token(self) -> None:
        """A round-trip succeeds and returns the expected payload fields."""
        user_id = uuid4()
        token, expires_in = create_access_token(user_id, settings)

        assert isinstance(token, str) and len(token) > 20
        assert expires_in == settings.jwt_access_token_expire_minutes * 60

        payload = decode_token(token, settings, expected_type="access")
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_decode_rejects_wrong_token_type(self) -> None:
        """decode_token raises when the token type does not match expected_type."""
        user_id = uuid4()
        token, _ = create_access_token(user_id, settings)

        with pytest.raises(AuthenticationRequiredError, match="Invalid token type"):
            decode_token(token, settings, expected_type="refresh")

    def test_decode_rejects_expired_token(self) -> None:
        """decode_token raises when the token's exp is in the past."""
        user_id = uuid4()
        one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
        expired_token = jwt.encode(
            {
                "sub": str(user_id),
                "type": "access",
                "iat": one_hour_ago - timedelta(minutes=1),
                "exp": one_hour_ago,
            },
            SECRET,
            algorithm=ALGORITHM,
        )

        with pytest.raises(
            AuthenticationRequiredError, match="Invalid or expired token"
        ):
            decode_token(expired_token, settings, expected_type="access")

    def test_decode_rejects_garbage_token(self) -> None:
        """decode_token raises when the token is not a valid JWT."""
        with pytest.raises(
            AuthenticationRequiredError, match="Invalid or expired token"
        ):
            decode_token("this-is-not-a-valid-jwt", settings, expected_type="access")


class TestRefreshToken:
    """create_refresh_token produces a valid token, UUID, and expiry."""

    def test_create_refresh_token_returns_expected_types(self) -> None:
        """The triple (token, token_id, expires_at) has the correct types."""
        token_str, token_id, expires_at = create_refresh_token(uuid4(), settings)

        assert isinstance(token_str, str) and len(token_str) > 20
        assert isinstance(token_id, type(uuid4()))
        assert isinstance(expires_at, datetime)
        assert expires_at.tzinfo is not None

    def test_decode_refresh_token_succeeds(self) -> None:
        """A refresh token can be decoded with type='refresh'."""
        user_id = uuid4()
        token_str, token_id, _ = create_refresh_token(user_id, settings)

        payload = decode_token(token_str, settings, expected_type="refresh")
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"
        assert payload["jti"] == str(token_id)


class TestCreateToken:
    """Direct _create_token edge cases."""

    def test_create_token_with_token_id(self) -> None:
        """When token_id is provided the payload includes a 'jti' claim."""
        user_id = uuid4()
        token_id = uuid4()
        token = _create_token(
            user_id=user_id,
            token_type="refresh",
            expires_delta=timedelta(days=7),
            settings=settings,
            token_id=token_id,
        )
        payload = decode_token(token, settings, expected_type="refresh")
        assert payload["jti"] == str(token_id)

    def test_create_token_without_token_id(self) -> None:
        """When token_id is omitted the payload has no 'jti' claim."""
        token = _create_token(
            user_id=uuid4(),
            token_type="access",
            expires_delta=timedelta(minutes=15),
            settings=settings,
        )
        payload = decode_token(token, settings, expected_type="access")
        assert "jti" not in payload


class TestTokenHashing:
    """hash_token — SHA-256 digest of the raw token."""

    def test_hash_token_length(self) -> None:
        """SHA-256 hex digest is exactly 64 characters."""
        digest = hash_token("some-arbitrary-token-string")
        assert isinstance(digest, str)
        assert len(digest) == 64

    def test_hash_token_deterministic(self) -> None:
        """Same input yields the same output every time."""
        token = "unique-test-token-value-abc-123"
        assert hash_token(token) == hash_token(token)

    def test_hash_token_different_inputs_different_outputs(self) -> None:
        """Different inputs produce different hashes (no collision)."""
        assert hash_token("token-a") != hash_token("token-b")
