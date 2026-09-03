"""Standard-library logging configuration with JSON output."""

import json
import logging

from app.core.config import Settings


class JSONFormatter(logging.Formatter):
    """Emit log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON string."""

        try:
            msg = record.getMessage()
        except Exception:
            msg = str(record.msg)

        fields = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": msg,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        return json.dumps(fields, default=str)


def configure_logging(settings: Settings) -> None:
    """Configure application logging once during application startup."""

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    logging.root.setLevel(getattr(logging, settings.log_level))
    logging.root.handlers = [handler]
