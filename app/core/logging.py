"""Logging configuration for the application."""

import logging
import sys
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str | None = None):
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
    """
    # Create logs directory if log_file is specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure format
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Basic config
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
    )

    # Configure uvicorn loggers to use our format
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        logging.getLogger(logger_name).handlers = handlers
        logging.getLogger(logger_name).propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)
