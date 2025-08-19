"""Logging setup for the application."""

from __future__ import annotations

__all__: tuple[str, ...] = ("setup_logging",)

import sys
from datetime import timedelta
from typing import TYPE_CHECKING

import logfire
from loguru import logger

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any


def scrubbing_callback(_m: logfire.ScrubMatch) -> Any | None:  # noqa: ANN401
    """Disable misbehaving scrubbing."""
    return None


def setup_logging() -> None:
    """Setup logging."""
    logfire.configure(scrubbing=logfire.ScrubbingOptions(callback=scrubbing_callback))
    logfire.instrument_pydantic()
    logfire.instrument_aiohttp_client()

    # Configure Loguru
    logger.remove()  # Remove default handler
    logger.configure(handlers=[logfire.loguru_handler()])
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level="DEBUG",
    )
    logger.add(
        "logs/gong_mcp_{time}.log",
        rotation=timedelta(days=1),
        retention=timedelta(days=30),
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} - {message}"
        ),
        level="DEBUG",
    )
