"""Rotating file logger for the application.

Never logs passwords or keyfile contents.
"""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

_MAX_BYTES = 2 * 1024 * 1024  # 2 MiB
_BACKUP_COUNT = 3
_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

_app_logger: logging.Logger | None = None


def get_app_logger(workspace_root: Path | None = None) -> logging.Logger:
    """Return the application logger, initializing it if needed."""
    global _app_logger
    if _app_logger is not None:
        return _app_logger

    logger = logging.getLogger("pcr.app")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        if workspace_root is not None:
            log_dir = workspace_root / "logs" / "app"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "app.log"
            handler: logging.Handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=_MAX_BYTES,
                backupCount=_BACKUP_COUNT,
                encoding="utf-8",
            )
        else:
            handler = logging.StreamHandler()

        handler.setFormatter(logging.Formatter(_FORMAT))
        logger.addHandler(handler)

    _app_logger = logger
    return logger


def reset_app_logger() -> None:
    """Reset logger (used in tests)."""
    global _app_logger
    if _app_logger:
        for h in list(_app_logger.handlers):
            _app_logger.removeHandler(h)
            h.close()
    _app_logger = None
