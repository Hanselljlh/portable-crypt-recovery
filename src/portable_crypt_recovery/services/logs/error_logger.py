"""Rotating file logger for unhandled errors and exceptions."""

from __future__ import annotations

import logging
import logging.handlers
import sys
import traceback
from pathlib import Path

_MAX_BYTES = 1 * 1024 * 1024  # 1 MiB
_BACKUP_COUNT = 2
_FORMAT = "%(asctime)s %(levelname)s: %(message)s"

_error_logger: logging.Logger | None = None


def get_error_logger(workspace_root: Path | None = None) -> logging.Logger:
    """Return the error logger, initializing it if needed."""
    global _error_logger
    if _error_logger is not None:
        return _error_logger

    logger = logging.getLogger("pcr.error")
    logger.setLevel(logging.ERROR)

    if not logger.handlers:
        if workspace_root is not None:
            log_dir = workspace_root / "logs" / "errors"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "error.log"
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

    _error_logger = logger
    return logger


def reset_error_logger() -> None:
    """Reset logger (used when switching workspaces)."""
    global _error_logger
    if _error_logger:
        for h in list(_error_logger.handlers):
            _error_logger.removeHandler(h)
            h.close()
    _error_logger = None


def install_excepthook(workspace_root: Path) -> None:
    """Install sys.excepthook to write unhandled exceptions to error.log.

    Safe to call multiple times — reinstalls the hook on each workspace open
    so it always points at the current workspace.
    """
    logger = get_error_logger(workspace_root)

    def _hook(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        logger.error("Unhandled exception:\n%s", tb_str)
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = _hook
