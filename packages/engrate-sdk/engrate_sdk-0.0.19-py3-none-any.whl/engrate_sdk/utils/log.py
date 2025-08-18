"""Logging utilities for pretty-printing, colorized, and context-managed logging.

This module provides:
- ANSI color and style helpers for log output
- A custom Formatter for enhanced log formatting
- Functions to initialize and configure logging
- Context manager for temporary log level changes
"""

import contextlib
import logging
import os
import re
from datetime import UTC, datetime
from typing import Any


def colorize(text: str, color_code: int) -> str:
    """Wraps text with the ANSI escape code for the given color."""
    return f"\033[{color_code}m{text}\033[39m"


def bold(text: str) -> str:
    """Bolds the given text."""
    return f"\033[1m{text}\033[22m"


def faint(text: str) -> str:
    """Faints the given text."""
    return f"\033[2m{text}\033[22m"


def italic(text: str) -> str:
    """Italicizes the given text."""
    return f"\033[3m{text}\033[23m"


def black(text: str) -> str:
    """Colors the given text black using ANSI escape codes."""
    return colorize(text, 30)


def red(text: str) -> str:
    """Colors the given text red using ANSI escape codes."""
    return colorize(text, 31)


def green(text: str) -> str:
    """Colors the given text green using ANSI escape codes."""
    return colorize(text, 32)


def yellow(text: str) -> str:
    """Colors the given text yellow using ANSI escape codes."""
    return colorize(text, 33)


def blue(text: str) -> str:
    """Colors the given text blue using ANSI escape codes."""
    return colorize(text, 34)


def magenta(text: str) -> str:
    """Colors the given text magenta using ANSI escape codes."""
    return colorize(text, 35)


def cyan(text: str) -> str:
    """Colors the given text cyan using ANSI escape codes."""
    return colorize(text, 36)


def white(text: str) -> str:
    """Colors the given text white using ANSI escape codes."""
    return colorize(text, 37)


CRITICAL = logging.CRITICAL
DEBUG = logging.DEBUG
ERROR = logging.ERROR
INFO = logging.INFO
WARNING = logging.WARNING

LEVEL_LABELS = {
    "CRITICAL": red(bold("CRITICAL")),
    "DEBUG": magenta("DEBUG"),
    "ERROR": red("ERROR"),
    "INFO": white("INFO"),
    "WARNING": yellow("WARNING"),
}


def strip_ansi(s: str) -> str:
    """Removes ANSI escape sequences from the given string."""
    r = re.compile(r"\x1B\[.*?[a-zA-Z]")
    return r.sub("", s)


def disp_len(s: str) -> int:
    """Returns the display length of the given string."""
    return len(strip_ansi(s))


def indent_rest(input_string: str, indent: int) -> str:
    """Indents all but the first line of the given string."""
    lines = input_string.split("\n")
    return "\n".join([lines[0]] + [f"{' ' * indent}{line}" for line in lines[1:]])


class Formatter(logging.Formatter):
    """Pretty-printing log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the specified record as a pretty-printed, colorized log message.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to be formatted.

        Returns:
        -------
        str
            The formatted log message string.
        """
        ts = (
            datetime.fromtimestamp(record.created, UTC).strftime(
                "%Y-%m-%dT%H:%M:%S.%f"
            )[:-3]
            + "Z"
        )
        level = LEVEL_LABELS.get(record.levelname, record.levelname)
        n = record.name
        color = sum([ord(x) for x in n]) % 6 + 32
        msg = record.getMessage()
        base = f"{italic(ts)} - {colorize(n, color)} - {level} - "
        ex = "\n" + self.formatException(record.exc_info) if record.exc_info else ""
        w = disp_len(base)
        return f"{base}{indent_rest(msg, w)}{indent_rest(ex, w)}"

    def format_exception(self, exc_info: Any) -> str:
        """Formats and returns the exception information as a string.

        Parameters
        ----------
        exc_info : tuple
            Exception information as returned by sys.exc_info().

        Returns:
        -------
        str
            The formatted exception string.
        """
        return super().formatException(exc_info)


def get_logger(name: str) -> logging.Logger:
    """Returns a logger with the specified name.

    Parameters
    ----------
    name : str
        The name of the logger to retrieve.

    Returns:
    -------
    logging.Logger
        The logger instance associated with the given name.
    """
    return logging.getLogger(name)


def set_level(level: int | str):
    """Sets the global log level."""
    if (isinstance(level, int) and level > 0) or level in logging._nameToLevel:  # type: ignore
        logging.getLogger().setLevel(level)
    else:
        logging.getLogger(__name__).warning("Invalid log level %s; ignoring.", level)


def init(level: str | int | None = None):
    """Initializes the logging system."""
    logging.captureWarnings(True)
    level = level or os.environ.get("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    set_level(level)


@contextlib.contextmanager
def level(level: int):
    """Temporarily modifies the log level.

    Usage:
    ```
    with log.level(log.DEBUG):
        ...
    ```.
    """
    logger = logging.getLogger()
    old_level = logger.level
    logger.setLevel(level)
    try:
        yield  # Yield control back to the calling block
    finally:
        logger.setLevel(old_level)  # Restore the original log level
