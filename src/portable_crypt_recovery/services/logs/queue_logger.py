"""Queue event logger."""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

_MAX_BYTES = 2 * 1024 * 1024  # 2 MiB
_BACKUP_COUNT = 3
_FORMAT = "%(asctime)s %(levelname)s: %(message)s"

_queue_logger: logging.Logger | None = None


def get_queue_logger(workspace_root: Path | None = None) -> logging.Logger:
    """Return the queue event logger, initializing it if needed."""
    global _queue_logger
    if _queue_logger is not None:
        return _queue_logger

    logger = logging.getLogger("pcr.queue")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        if workspace_root is not None:
            log_dir = workspace_root / "logs" / "queue"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "queue.log"
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

    _queue_logger = logger
    return logger


def reset_queue_logger() -> None:
    """Reset logger (used in tests)."""
    global _queue_logger
    if _queue_logger:
        for h in list(_queue_logger.handlers):
            _queue_logger.removeHandler(h)
            h.close()
    _queue_logger = None
