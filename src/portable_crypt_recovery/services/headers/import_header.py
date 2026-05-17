"""Import a user-provided header file into the workspace."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Callable

from portable_crypt_recovery.core.ids import new_id
from portable_crypt_recovery.core.paths import to_workspace_relative
from portable_crypt_recovery.core.timestamps import utc_now_iso
from portable_crypt_recovery.models.header import HEADER_SIZE_BYTES, Header

# If the import file is larger than this we refuse it entirely
MAX_IMPORT_SIZE = 131072  # 128 KiB


def _sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def import_header_file(
    source: Path,
    workspace_root: Path,
    target_id: str,
    candidate_type: str = "unknown_imported_header",
    pick_offset_callback: Callable[[list[tuple[int, str]]], int] | None = None,
    notes: str = "",
) -> Header:
    """Import a header file and write a normalized 512-byte copy to the workspace.

    Parameters
    ----------
    source:
        User-provided header file (never modified).
    workspace_root:
        Workspace root directory.
    target_id:
        ID of the target this header belongs to.
    candidate_type:
        Header role, defaults to "unknown_imported_header".
    pick_offset_callback:
        Called when the source is > 512 bytes and ≤ 131072 bytes.
        Receives a list of (offset, description) tuples and must return
        the chosen byte offset. Defaults to returning offset 0.
    notes:
        Optional notes for the header record.

    Returns
    -------
    Header
        The model for the imported and normalized header.
    """
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"Source header file not found: {source}")

    raw = source.read_bytes()
    file_size = len(raw)

    if file_size == 0:
        raise ValueError("Source header file is empty.")

    if file_size > MAX_IMPORT_SIZE:
        raise ValueError(
            f"Source header file is too large ({file_size} bytes). "
            f"Maximum accepted size is {MAX_IMPORT_SIZE} bytes."
        )

    if file_size == HEADER_SIZE_BYTES:
        data_512 = raw
    else:
        # Build candidate list: every 512-byte-aligned offset
        candidates: list[tuple[int, str]] = []
        for offset in range(0, file_size - HEADER_SIZE_BYTES + 1, HEADER_SIZE_BYTES):
            candidates.append((offset, f"Offset {offset}"))

        if not candidates:
            raise ValueError(
                f"File is {file_size} bytes — could not find any 512-byte-aligned candidates."
            )

        if pick_offset_callback is not None:
            chosen_offset = pick_offset_callback(candidates)
        else:
            chosen_offset = 0

        data_512 = raw[chosen_offset : chosen_offset + HEADER_SIZE_BYTES]
        if len(data_512) != HEADER_SIZE_BYTES:
            raise ValueError(f"Extracted slice at offset {chosen_offset} is not 512 bytes.")

    sha256 = _sha256_of(data_512)
    header_id = new_id("header")
    normalized_dir = workspace_root / "headers" / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)
    normalized_path = normalized_dir / f"header_{header_id}.bin"
    normalized_path.write_bytes(data_512)

    # Copy original to imported/
    imported_dir = workspace_root / "headers" / "imported"
    imported_dir.mkdir(parents=True, exist_ok=True)
    imported_copy = imported_dir / f"header_{header_id}_original{source.suffix}"
    shutil.copy2(source, imported_copy)

    rel_path = to_workspace_relative(normalized_path, workspace_root)

    return Header(
        header_id=header_id,
        target_id=target_id,
        source_type="imported",
        workspace_relative_path=rel_path,
        size_bytes=HEADER_SIZE_BYTES,
        sha256=sha256,
        extraction_timestamp=utc_now_iso(),
        candidate_type=candidate_type,
        notes=notes,
    )
