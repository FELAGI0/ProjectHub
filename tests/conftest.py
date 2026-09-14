"""Shared test configuration."""

import os

import pytest

from app.core.rate_limit import limiter

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough")


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Reset rate limiter storage before and after each test."""
    limiter.reset()
    yield
    limiter.reset()
