"""Startup helpers for the portable folder layout."""

from __future__ import annotations

from pathlib import Path

from portable_crypt_recovery.core.paths import app_root_from_cwd

PORTABLE_DIRS = (
    "app",
    "tools/hashcat",
    "workspaces/default",
    "config",
    "logs",
    "docs",
)


def ensure_default_portable_layout(root: Path | None = None) -> Path:
    """Create the default PCR portable folders when they are missing.

    The function only creates folders. It does not create or move sensitive recovery data.
    """
    base = root or app_root_from_cwd()
    for folder in PORTABLE_DIRS:
        (base / folder).mkdir(parents=True, exist_ok=True)
    return base
