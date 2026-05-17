"""Recent workspaces list management."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from portable_crypt_recovery.core.atomic_write import atomic_write_json
from portable_crypt_recovery.core.timestamps import utc_now_iso

MAX_RECENT = 10


def _recent_path(config_dir: Path) -> Path:
    return config_dir / "recent-workspaces.json"


def _load_recent(config_dir: Path) -> list[dict[str, Any]]:
    path = _recent_path(config_dir)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("workspaces", [])


def _save_recent(config_dir: Path, workspaces: list[dict[str, Any]]) -> None:
    config_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(_recent_path(config_dir), {"schema_version": 1, "workspaces": workspaces})


def record_workspace(config_dir: Path, workspace_root: Path, name: str) -> None:
    """Add or update a workspace in the recent list.

    Only stores: path, name, timestamp. No sensitive data.
    """
    workspaces = _load_recent(config_dir)
    path_str = str(workspace_root.resolve())

    # Remove existing entry for this path
    workspaces = [w for w in workspaces if w.get("path") != path_str]

    # Insert at front
    workspaces.insert(
        0,
        {
            "path": path_str,
            "name": name,
            "last_opened_timestamp": utc_now_iso(),
        },
    )

    # Trim to max
    workspaces = workspaces[:MAX_RECENT]
    _save_recent(config_dir, workspaces)


def get_recent_workspaces(config_dir: Path) -> list[dict[str, Any]]:
    """Return recent workspace entries (path, name, timestamp)."""
    return _load_recent(config_dir)


def remove_workspace(config_dir: Path, workspace_root: Path) -> None:
    """Remove a workspace from the recent list."""
    path_str = str(workspace_root.resolve())
    workspaces = [w for w in _load_recent(config_dir) if w.get("path") != path_str]
    _save_recent(config_dir, workspaces)
