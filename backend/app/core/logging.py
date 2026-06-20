"""Structured logging configuration using structlog.

Configures application-wide logging to output structured JSON logs
in production and human-readable colored logs in development.
"""

import logging
import sys

import structlog

from app.core.config import settings


def configure_logging() -> None:
    """Configure structlog for the application.

    Sets up either JSON output (production) or pretty console output
    (development) based on the current APP_ENV setting. Must be called
    once at application startup, before any loggers are used.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.is_production:
        # Production: structured JSON logs for log aggregation tools
        renderer = structlog.processors.JSONRenderer()
    else:
        # Development: human-readable colored console output
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors
        + [
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a configured structlog logger instance.

    Args:
        name: The name of the logger, typically __name__ of the calling module.

    Returns:
        A bound structlog logger ready to use.
    """
    return structlog.get_logger(name)