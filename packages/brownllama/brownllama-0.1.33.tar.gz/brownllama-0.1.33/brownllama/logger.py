"""
A module providing configurable logger setup for applications and libraries.

This module configures both the root logger and common third-party library loggers
with consistent settings to ensure uniform logging behavior.
"""

import logging
import os
import sys
from logging import Logger
from typing import ClassVar

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# A set of common third-party libraries whose logging levels we want to control.
LIBRARIES: set[str] = {
    "requests",
    "urllib3",
    "httpcore",
    "uwsgi",
    "gunicorn",
    "celery",
    "starlette",
    "uvicorn",
    "fastapi",
    "google.api_core",
    "google.cloud",
    "google.genai",
    "pydantic",
    "pandas",
    "brownllama",
}


class ColorFormatter(logging.Formatter):
    """
    Custom formatter that colors the entire log prefix (timestamp | level | name |).

    This version is enhanced to use a different color for DEBUG logs originating
    from third-party libraries.
    """

    COLORS: ClassVar[dict[int, str]] = {
        logging.DEBUG: "\033[95m",  # Purple
        logging.INFO: "\033[34m",  # Blue
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[1;31m",  # Bold Red
    }
    # Bright Cyan for DEBUG logs from third-party libraries
    LIBRARY_DEBUG_COLOR: ClassVar[str] = "\033[36m"
    RESET: ClassVar[str] = "\033[0m"

    # Expected number of parts in log format: timestamp | level | name | message
    _EXPECTED_LOG_PARTS: ClassVar[int] = 4

    def __init__(self, fmt: str, library_names: set[str]) -> None:
        """
        Initialize the formatter with color support and library names.

        Args:
            fmt: The format string for the log message.
            library_names: A set of logger names that should be considered
                           third-party libraries.

        """
        super().__init__(fmt)
        # Simple TTY check for color support
        self.use_colors = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
        self.library_names = library_names

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with colors for the prefix.

        Args:
            record: The log record to format.

        Returns:
            str: The formatted log record.

        """
        formatted = super().format(record)

        if not self.use_colors:
            return formatted

        # Determine the color to use.
        # Check if the log is a DEBUG level from a library.
        if record.levelno == logging.DEBUG and any(
            record.name.startswith(lib) for lib in self.library_names
        ):
            color = self.LIBRARY_DEBUG_COLOR
        else:
            # Otherwise, use the standard color for the log level.
            color = self.COLORS.get(record.levelno, self.RESET)

        # Split at the first " | " after the prefix (timestamp | level | name) to separate from message.
        parts = formatted.split(" | ", self._EXPECTED_LOG_PARTS - 1)

        if len(parts) == self._EXPECTED_LOG_PARTS:
            # Reconstruct the full prefix string to be colored, including the last " | "
            colored_prefix_str = f"{parts[0]} | {parts[1]} | {parts[2]} | "
            message = parts[3]

            # Apply color to the full prefix including the last '|', then reset, then append message.
            return f"{color}{colored_prefix_str}{self.RESET}{message}"

        return formatted


class LlamaLogger:
    """Simple logger configuration that auto-detects dev/prod mode."""

    _configured: ClassVar[bool] = False
    _app_level: ClassVar[int] = logging.INFO

    @classmethod
    def _is_dev_mode(cls) -> bool:
        """
        Check if we're running on Cloud Run (production) or local (development).

        Returns:
            bool: True if we're running on Cloud Run, False otherwise

        """
        # Allow LOCAL_INFO=1 to test INFO mode locally
        if os.getenv("LOCAL_INFO", "").lower() in {"1", "true", "yes"}:
            return False
        # Check running on Cloud Run
        return not bool(os.getenv("K_SERVICE"))

    @classmethod
    def configure_logging(cls, dev_mode: bool | None = None) -> None:
        """
        Configure logging once. Libraries=DEBUG, App=DEBUG if dev else INFO.

        Args:
            dev_mode: Explicitly set the logging mode. If None, it will be
                auto-detected based on the environment.

        """
        if cls._configured:
            return

        if dev_mode is None:
            dev_mode = cls._is_dev_mode()

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        root.handlers.clear()

        # Console handler with colored formatter
        handler = logging.StreamHandler()
        # Instantiate the custom formatter and pass the list of library names
        formatter = ColorFormatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            library_names=LIBRARIES,
        )
        handler.setFormatter(formatter)
        root.addHandler(handler)

        # This loop explicitly sets 3rd party libraries to DEBUG.
        # This is the key part that ensures they always show debug logs.
        for lib in LIBRARIES:
            logging.getLogger(lib).setLevel(logging.DEBUG)

        # Store app level
        cls._app_level = logging.DEBUG if dev_mode else logging.INFO
        cls._configured = True

    @classmethod
    def get_logger(cls, name: str, level: int | str | None = None) -> Logger:
        """
        Get logger for app code. Auto-configures if needed.

        Args:
            name: The name of the logger, typically __name__.
            level: The logging level to set for this logger. If None, the
                default app level is used.

        Returns:
            A configured logging.Logger instance.

        """
        if not cls._configured:
            cls.configure_logging()

        logger = logging.getLogger(name)

        # Handle string levels
        if isinstance(level, str):
            level = getattr(logging, level.upper())

        logger.setLevel(level if level is not None else cls._app_level)

        return logger


def configure_logging(dev_mode: bool | None = None) -> None:
    """
    Configure logging once. Libraries=DEBUG, App=DEBUG if dev else INFO.

    Args:
        dev_mode: Explicitly set the logging mode. If None, it will be
            auto-detected based on the environment.

    """
    LlamaLogger.configure_logging(dev_mode)


def get_logger(name: str, level: int | str | None = None) -> Logger:
    """
    Get logger for app code. Auto-configures if needed.

    Args:
        name: The name of the logger, typically __name__.
        level: The logging level to set for this logger. If None, the
            default app level is used.

    Returns:
        A configured logging.Logger instance.

    """
    return LlamaLogger.get_logger(name, level)
