"""Header metadata persistence."""

from __future__ import annotations

import json
from pathlib import Path

from portable_crypt_recovery.core.atomic_write import atomic_write_json
from portable_crypt_recovery.models.header import Header


def _metadata_path(workspace_root: Path, header_id: str) -> Path:
    return workspace_root / "headers" / "metadata" / f"header_{header_id}.json"


def save_header_metadata(workspace_root: Path, header: Header) -> None:
    """Write header metadata JSON to headers/metadata/<header_id>.json."""
    path = _metadata_path(workspace_root, header.header_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(path, header.to_dict())


def load_header_metadata(workspace_root: Path, header_id: str) -> Header:
    """Read header metadata from JSON and return a Header model."""
    path = _metadata_path(workspace_root, header_id)
    if not path.exists():
        raise FileNotFoundError(f"Header metadata not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Header.from_dict(data)


def list_header_ids(workspace_root: Path) -> list[str]:
    """Return all header IDs found in headers/metadata/."""
    metadata_dir = workspace_root / "headers" / "metadata"
    if not metadata_dir.exists():
        return []
    return [
        p.stem.removeprefix("header_")
        for p in metadata_dir.iterdir()
        if p.suffix == ".json" and p.stem.startswith("header_")
    ]
