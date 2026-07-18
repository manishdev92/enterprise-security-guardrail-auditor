"""Structured JSON logging configuration for the backend service."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from app.core.config import Settings


class JsonFormatter(logging.Formatter):
    """Format log records as JSON for machine-readable logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        for key, value in record.__dict__.items():
            if key not in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            }:
                payload[key] = value

        return json.dumps(payload, default=str)


def configure_logging(settings: Settings | None = None) -> logging.Logger:
    """Configure root logging once and return the application logger."""
    effective_settings = settings or Settings.from_env()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.setLevel(
        getattr(logging, effective_settings.log_level.upper(), logging.INFO)
    )
    root_logger.propagate = False

    logger = logging.getLogger("app")
    logger.setLevel(root_logger.level)
    logger.propagate = False
    logger.handlers = [handler]
    return logger


def get_logger(name: str) -> logging.Logger:
    """Return a named logger that uses the configured formatting."""
    return logging.getLogger(name)
