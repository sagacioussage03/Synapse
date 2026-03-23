"""
Synapse – Centralized Logging
Writes to backend/synapse.log (clean-slate on every restart).
If the log grows beyond 10 MB while running, it is truncated automatically.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "synapse.log")
MAX_BYTES = 10 * 1024 * 1024  # 10 MB

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return the root 'synapse' logger.
    - Clears the log file on every startup (clean-slate).
    - RotatingFileHandler with backupCount=0 ensures the single file
      is truncated when it exceeds MAX_BYTES (no old copies kept).
    - Also streams to stdout so uvicorn console stays useful.
    """
    # Wipe previous log on startup
    if os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()

    logger = logging.getLogger("synapse")
    logger.setLevel(level)

    # Avoid duplicate handlers on reload
    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # File handler – auto-truncates at MAX_BYTES, keeps 0 backups
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_BYTES, backupCount=0, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = "synapse") -> logging.Logger:
    """Return a child logger under the 'synapse' namespace."""
    return logging.getLogger(f"synapse.{name}")
