"""Stable ID generation."""

from __future__ import annotations

import secrets


def new_id(prefix: str) -> str:
    """Return a short stable ID using a safe prefix."""
    clean_prefix = "".join(ch for ch in prefix.lower() if ch.isalnum() or ch == "_").strip("_")
    if not clean_prefix:
        clean_prefix = "id"
    return f"{clean_prefix}_{secrets.token_hex(6)}"
