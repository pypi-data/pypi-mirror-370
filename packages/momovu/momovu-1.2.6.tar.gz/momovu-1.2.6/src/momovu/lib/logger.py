"""Enhanced logging configuration for Momovu.

This module provides structured logging with context, performance metrics,
and decorators for common operations.
"""

import json
import logging

_console_logging_enabled = False


class StructuredFormatter(logging.Formatter):
    """Formatter that outputs structured log messages with context."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with structured context."""
        message = super().format(record)

        if hasattr(record, "context") and record.context:
            context_str = json.dumps(record.context, default=str)
            message = f"{message} | context={context_str}"

        return message


def configure_logging(verbose: int = 0, debug: bool = False) -> None:
    """Configure logging based on command line arguments.

    Args:
        verbose: Verbosity level (0=WARNING, 1=INFO, 2+=DEBUG)
        debug: Enable debug logging
    """
    global _console_logging_enabled

    if debug or verbose >= 2:
        log_level = logging.DEBUG
    elif verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    _console_logging_enabled = verbose > 0 or debug

    root_logger = logging.getLogger()
    try:
        handlers_copy = list(root_logger.handlers)
        for handler in handlers_copy:
            root_logger.removeHandler(handler)
    except (TypeError, AttributeError):
        # In case we're in a test environment with mocked logger
        pass

    if _console_logging_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = StructuredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        root_logger.addHandler(console_handler)
        root_logger.setLevel(log_level)
    else:
        null_handler = logging.NullHandler()
        root_logger.addHandler(null_handler)
        root_logger.setLevel(logging.WARNING)

    logging.getLogger("PySide6").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    # Don't add handlers or set levels here - let the root logger configuration handle it
    return logger
