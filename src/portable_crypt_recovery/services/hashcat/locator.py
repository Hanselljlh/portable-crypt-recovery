"""Hashcat locator."""

from __future__ import annotations

import shutil
from pathlib import Path

HASHCAT_EXECUTABLE_NAMES = ("hashcat.exe", "hashcat", "hashcat.bin")


def portable_hashcat_candidates(portable_root: Path) -> list[Path]:
    base = portable_root / "tools" / "hashcat"
    return [base / name for name in HASHCAT_EXECUTABLE_NAMES]


def find_in_portable_tools(portable_root: Path) -> Path | None:
    for candidate in portable_hashcat_candidates(portable_root):
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def find_on_path() -> Path | None:
    for name in HASHCAT_EXECUTABLE_NAMES:
        found = shutil.which(name)
        if found:
            return Path(found).resolve()
    return None
