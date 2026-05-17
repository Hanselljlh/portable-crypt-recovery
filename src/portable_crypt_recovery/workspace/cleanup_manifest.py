"""Cleanup manifest management."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from portable_crypt_recovery.core.atomic_write import atomic_write_json
from portable_crypt_recovery.core.timestamps import utc_now_iso

MANIFEST_PATH_PARTS = ("cleanup", "cleanup-manifest.json")


def _manifest_path(workspace_root: Path) -> Path:
    return workspace_root.joinpath(*MANIFEST_PATH_PARTS)


def _load_manifest(workspace_root: Path) -> dict[str, Any]:
    path = _manifest_path(workspace_root)
    if not path.exists():
        return {"schema_version": 1, "entries": []}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_manifest(workspace_root: Path, data: dict[str, Any]) -> None:
    atomic_write_json(_manifest_path(workspace_root), data)


def add_entry(
    workspace_root: Path,
    relative_path: str,
    category: str,
    description: str = "",
    created_by: str = "",
) -> dict[str, Any]:
    """Add a file entry to the cleanup manifest and save it.

    Parameters
    ----------
    workspace_root:
        Root of the workspace.
    relative_path:
        POSIX-style path relative to workspace root.
    category:
        Category label (e.g. "normalized_keyfile", "generated_wordlist").
    description:
        Optional human-readable description.
    created_by:
        Optional source identifier (step name or module).
    """
    manifest = _load_manifest(workspace_root)
    entry: dict[str, Any] = {
        "relative_path": relative_path,
        "category": category,
        "description": description,
        "created_by": created_by,
        "added_timestamp": utc_now_iso(),
        "status": "active",
    }
    manifest["entries"].append(entry)
    _save_manifest(workspace_root, manifest)
    return entry


def list_entries(workspace_root: Path) -> list[dict[str, Any]]:
    """Return all entries from the cleanup manifest."""
    return _load_manifest(workspace_root).get("entries", [])


def update_entry_status(
    workspace_root: Path,
    relative_path: str,
    status: str,
) -> bool:
    """Update the status of an existing manifest entry. Returns True if found."""
    manifest = _load_manifest(workspace_root)
    found = False
    for entry in manifest["entries"]:
        if entry.get("relative_path") == relative_path:
            entry["status"] = status
            found = True
    if found:
        _save_manifest(workspace_root, manifest)
    return found
