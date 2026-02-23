"""Structured logging utilities."""

from __future__ import annotations

import json
import logging
from typing import Any


class JsonFormatter(logging.Formatter):
    """Format logs as JSON records."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
        }
        if hasattr(record, "extra_data"):
            payload["extra"] = getattr(record, "extra_data")
        return json.dumps(payload, default=str)


def get_logger(name: str = "forgeai", level: int = logging.INFO) -> logging.Logger:
    """Build or return a configured structured logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def bind_logger(logger: logging.Logger, **fields: object) -> logging.LoggerAdapter:
    """Attach constant structured fields to every log entry."""
    return logging.LoggerAdapter(logger, extra={"extra_data": fields})
