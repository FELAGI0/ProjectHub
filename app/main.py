"""ASGI application entry point."""

from app.db import registry  # noqa: F401
from app.factory import create_application

app = create_application()
