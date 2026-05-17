"""Atomic file write helpers that stay inside the destination folder."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


def atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Atomically write text using a temporary file in the destination directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        "w",
        encoding=encoding,
        dir=path.parent,
        delete=False,
        prefix=f".{path.name}.",
        suffix=".tmp",
    ) as tmp:
        tmp.write(content)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_name = tmp.name
    os.replace(tmp_name, path)


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    """Atomically write JSON with stable formatting."""
    atomic_write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n")
