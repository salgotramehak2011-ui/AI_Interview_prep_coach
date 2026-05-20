"""Loguru-based logging configuration."""

import sys
from pathlib import Path

from loguru import logger

from app.config import get_settings


def setup_logging() -> None:
    """Configure application logging with console and file sinks."""
    settings = get_settings()
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        format=log_format,
        level="DEBUG" if settings.DEBUG else "INFO",
        colorize=True,
    )

    logger.add(
        settings.LOGS_DIR / "app_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="14 days",
        compression="zip",
        level="DEBUG",
        format=log_format,
        enqueue=True,
    )

    logger.info("Logging initialized for {}", settings.APP_NAME)


def get_logger(name: str = __name__):
    """Return a bound logger instance."""
    return logger.bind(module=name)
