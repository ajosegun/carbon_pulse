"""Loguru logger configuration for Carbon Pulse."""

import sys
from pathlib import Path

from loguru import logger

from carbon_pulse.config import settings


def setup_logger():
    """Configure loguru logger with custom settings."""
    # Remove default handler
    logger.remove()

    # Create logs directory if it doesn't exist
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Add console handler with custom format
    logger.add(
        sys.stdout,
        format=settings.log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # Add file handler if log_file is specified
    if settings.log_file:
        logger.add(
            settings.log_file,
            format=settings.log_format,
            level=settings.log_level,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True,
        )

    # Intercept standard logging
    logger.add(
        sys.stderr,
        format=settings.log_format,
        level=settings.log_level,
        filter=lambda record: record["extra"].get("name") == "uvicorn",
    )


# Initialize logger
setup_logger()

# Export logger instance
__all__ = ["logger"]
