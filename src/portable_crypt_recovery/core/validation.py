"""Validation helpers."""

from __future__ import annotations

from pathlib import Path

from portable_crypt_recovery.core.paths import is_relative_to


def require_inside_workspace(path: Path, workspace_root: Path) -> None:
    """Raise if a path is outside the selected workspace."""
    if not is_relative_to(path, workspace_root):
        raise ValueError(f"Path must stay inside workspace: {path}")


def require_readable_file(path: Path) -> None:
    """Raise if a path is not a readable file."""
    if not path.exists():
        raise FileNotFoundError(path)
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
