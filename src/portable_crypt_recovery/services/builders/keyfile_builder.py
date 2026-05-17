"""Keyfile normalization foundation."""

from __future__ import annotations

from pathlib import Path

KEYFILE_USED_BYTES_LIMIT = 1_048_576


def normalize_keyfile(source: Path, destination: Path) -> bool:
    """Copy the bytes used by VeraCrypt/TrueCrypt keyfile handling.

    Returns True when the source was capped to the first 1 MiB.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as src:
        data = src.read(KEYFILE_USED_BYTES_LIMIT + 1)
    capped = len(data) > KEYFILE_USED_BYTES_LIMIT
    destination.write_bytes(data[:KEYFILE_USED_BYTES_LIMIT])
    return capped
