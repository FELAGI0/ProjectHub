"""HTTP middleware for request correlation and access logs."""

import re
import time
from uuid import uuid4

import structlog
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = structlog.get_logger(__name__)
_REQUEST_ID_PATTERN = re.compile(r"^[a-zA-Z0-9\-_.]{1,128}$")


class RequestIDMiddleware:
    """Bind a request ID and add it to every HTTP response."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = Headers(scope=scope).get("X-Request-ID")
        if incoming and _REQUEST_ID_PATTERN.fullmatch(incoming):
            request_id = incoming
        else:
            request_id = str(uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        started_at = time.perf_counter()
        status_code: int | None = None
        response_started = False

        async def send_with_request_id(message: Message) -> None:
            nonlocal response_started, status_code
            if message["type"] == "http.response.start" and not response_started:
                response_started = True
                status_code = message["status"]
                headers = list(message.get("headers", []))
                headers = [
                    (name, value)
                    for name, value in headers
                    if name.lower() != b"x-request-id"
                ]
                headers.append((b"x-request-id", request_id.encode()))
                message = {**message, "headers": headers}
            await send(message)

        logger.info(
            "request_started",
            method=scope["method"],
            path=scope["path"],
        )
        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            logger.info(
                "request_finished",
                method=scope["method"],
                path=scope["path"],
                status_code=status_code,
                duration_ms=round((time.perf_counter() - started_at) * 1000, 2),
            )
            structlog.contextvars.clear_contextvars()
