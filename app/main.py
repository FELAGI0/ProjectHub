"""ASGI application entry point."""

from app.factory import create_application

app = create_application()
