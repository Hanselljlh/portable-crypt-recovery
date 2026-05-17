"""Path helpers."""

from __future__ import annotations

from pathlib import Path


def app_root_from_cwd() -> Path:
    """Return the current working directory as the portable root."""
    return Path.cwd().resolve()


def is_relative_to(path: Path, base: Path) -> bool:
    """Compatibility wrapper for Path.is_relative_to with resolved paths."""
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def to_workspace_relative(path: Path, workspace_root: Path) -> str:
    """Return a POSIX-style workspace-relative path."""
    resolved = path.resolve()
    root = workspace_root.resolve()
    if not is_relative_to(resolved, root):
        raise ValueError(f"Path is outside workspace: {path}")
    return resolved.relative_to(root).as_posix()


def safe_join_workspace(workspace_root: Path, relative_path: str) -> Path:
    """Join a relative path to a workspace and reject traversal outside it."""
    candidate = (workspace_root / relative_path).resolve()
    if not is_relative_to(candidate, workspace_root):
        raise ValueError(f"Path escapes workspace: {relative_path}")
    return candidate
