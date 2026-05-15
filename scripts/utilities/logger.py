"""Centralised logging configuration for the analytics platform."""
import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def get_logger(name: str, log_file: Optional[str] = None, level: str = "INFO") -> logging.Logger:
    """Return a configured logger.

    Args:
        name: Logger name (usually __name__).
        log_file: Optional path to a rotating log file.
        level: Logging level string.

    Returns:
        Configured :class:`logging.Logger`.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        fh = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
        )
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger
