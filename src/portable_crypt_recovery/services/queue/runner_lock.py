"""Runner lock to prevent duplicate queue runners per workspace."""

from __future__ import annotations

import json
import os
from pathlib import Path

from portable_crypt_recovery.core.atomic_write import atomic_write_json
from portable_crypt_recovery.core.timestamps import utc_now_iso

_LOCK_FILE = "queue/runner-lock.json"


def _lock_path(workspace_root: Path) -> Path:
    return workspace_root / _LOCK_FILE


def acquire_lock(workspace_root: Path) -> bool:
    """Attempt to acquire the runner lock.

    Returns True if lock was acquired, False if already locked by another process.
    """
    lock_file = _lock_path(workspace_root)

    # Check if a lock file already exists and the PID is still alive
    if lock_file.exists():
        try:
            with lock_file.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            pid = int(data.get("pid", 0))
            if pid and _pid_alive(pid):
                return False
        except (json.JSONDecodeError, ValueError, OSError):
            pass  # Stale lock — overwrite it

    lock_file.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(
        lock_file,
        {
            "schema_version": 1,
            "pid": os.getpid(),
            "acquired_timestamp": utc_now_iso(),
        },
    )
    return True


def release_lock(workspace_root: Path) -> None:
    """Release the runner lock if it belongs to this process."""
    lock_file = _lock_path(workspace_root)
    if not lock_file.exists():
        return
    try:
        with lock_file.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if int(data.get("pid", 0)) == os.getpid():
            lock_file.unlink(missing_ok=True)
    except (json.JSONDecodeError, ValueError, OSError):
        lock_file.unlink(missing_ok=True)


def is_locked(workspace_root: Path) -> bool:
    """Return True if another process holds the runner lock."""
    lock_file = _lock_path(workspace_root)
    if not lock_file.exists():
        return False
    try:
        with lock_file.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        pid = int(data.get("pid", 0))
        return pid != os.getpid() and _pid_alive(pid)
    except (json.JSONDecodeError, ValueError, OSError):
        return False


def _pid_alive(pid: int) -> bool:
    """Return True if the given PID exists."""
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False
    except OSError:
        return True  # err on the side of caution
