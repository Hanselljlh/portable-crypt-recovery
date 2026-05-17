"""Workspace creation, opening, and repair."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from portable_crypt_recovery.core.atomic_write import atomic_write_json
from portable_crypt_recovery.workspace.workspace_paths import WORKSPACE_DIRS
from portable_crypt_recovery.workspace.workspace_schema import (
    default_settings_record,
    empty_cleanup_manifest_record,
    empty_queue_state_record,
    empty_targets_record,
    new_workspace_record,
)


@dataclass(slots=True)
class Workspace:
    """Opened workspace."""

    root: Path
    record: dict

    @property
    def name(self) -> str:
        return str(self.record.get("workspace_name", self.root.name))


def ensure_workspace_dirs(root: Path) -> None:
    """Create all required workspace folders."""
    for folder in WORKSPACE_DIRS:
        (root / folder).mkdir(parents=True, exist_ok=True)


def create_workspace(root: Path, name: str | None = None) -> Workspace:
    """Create or initialize a workspace at root."""
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    ensure_workspace_dirs(root)

    workspace_record = new_workspace_record(name or root.name)
    atomic_write_json(root / "workspace.json", workspace_record)
    atomic_write_json(root / "settings.json", default_settings_record())
    atomic_write_json(root / "targets" / "targets.json", empty_targets_record())
    atomic_write_json(root / "queue" / "queue-state.json", empty_queue_state_record())
    atomic_write_json(root / "cleanup" / "cleanup-manifest.json", empty_cleanup_manifest_record())
    return Workspace(root=root, record=workspace_record)


def open_workspace(root: Path, repair: bool = True) -> Workspace:
    """Open an existing workspace, optionally repairing missing folders."""
    root = root.resolve()
    workspace_file = root / "workspace.json"
    if not workspace_file.exists():
        raise FileNotFoundError(f"Missing workspace.json: {workspace_file}")
    if repair:
        ensure_workspace_dirs(root)
    with workspace_file.open("r", encoding="utf-8") as handle:
        record = json.load(handle)
    return Workspace(root=root, record=record)


def create_or_open_workspace(root: Path, name: str | None = None) -> Workspace:
    """Open a valid workspace or create a new one if no workspace file exists."""
    if (root / "workspace.json").exists():
        return open_workspace(root)
    return create_workspace(root, name=name)
