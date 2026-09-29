import logging
from pathlib import Path

from src.config.settings import settings
from src.utils.pii import PiiLogFilter

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def _get_log_level():
    """
    Turn the LOG_LEVEL setting (e.g. "INFO", "debug") into a logging level.
    If the value is not a real level name we fall back to INFO instead of crashing.
    """
    level = logging.getLevelName(settings.log_level.strip().upper())
    if isinstance(level, int):
        return level
    return logging.INFO


def get_logger(name):
    """Return a logger that writes to both the console and logs/app.log."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(_get_log_level())

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(PiiLogFilter())
    logger.addHandler(console_handler)

    LOG_DIR.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(PiiLogFilter())
    logger.addHandler(file_handler)

    return logger