"""
SkillBridge AI — Logging Configuration

Configures structured logging for the application.
Logs are written to stdout/stderr. No PII is logged.
"""

import logging
import sys


def setup_logging(debug: bool = False) -> None:
    """Configure application logging.

    Args:
        debug: If True, set log level to DEBUG; otherwise INFO. Defaults to
            False so calling without arguments does not enable verbose
            logging (matches the safe DEBUG=False config default).
    """
    level = logging.DEBUG if debug else logging.INFO

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove any existing handlers to avoid duplicate logs
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    # Console handler with structured format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if debug else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.

    Args:
        name: Logger name (typically __name__).

    Returns:
        A configured Logger instance.
    """
    return logging.getLogger(name)
