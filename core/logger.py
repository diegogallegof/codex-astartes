import logging
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "chapter.log")


def _setup_logger():
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("codex_astartes")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = _setup_logger()


def log_threat(threat):
    """Write a Threat to the chapter log."""
    logger.log(
        _severity_to_level(threat.severity.value),
        f"[{threat.agent}] {threat.description} | meta={threat.metadata}",
    )


def log_event(message: str):
    """Write a plain operational event to the chapter log."""
    logger.info(f"[CHAPTER] {message}")


def _severity_to_level(severity: str) -> int:
    return {
        "LOW":      logging.INFO,
        "MEDIUM":   logging.WARNING,
        "HIGH":     logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }.get(severity, logging.INFO)
