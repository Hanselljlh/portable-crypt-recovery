"""Header extraction from VeraCrypt/TrueCrypt container files.

All source access is read-only. The source file is never modified.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import NamedTuple

# Byte offsets for header candidates within a container/image
OFFSET_NORMAL_VOLUME = 0          # standard outer/normal volume header
OFFSET_HIDDEN_VOLUME = 65536      # hidden volume header
OFFSET_NORMAL_SYSTEM = 31744     # system partition/boot header

HEADER_SIZE = 512


class ExtractionCandidate(NamedTuple):
    candidate_type: str  # "normal_volume_header" | "hidden_volume_header" | "normal_system_header"
    offset: int
    data: bytes
    sha256: str


def _open_source_readonly(source: Path) -> None:
    """Validate the source can be opened for reading."""
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    if not source.is_file():
        raise ValueError(f"Source path is not a file: {source}")
    # Attempt open to validate access
    with source.open("rb") as _:
        pass


def _read_slice(source: Path, offset: int, size: int) -> bytes:
    """Read a slice from source at the given offset, read-only."""
    with source.open("rb") as fh:
        fh.seek(offset)
        data = fh.read(size)
    if len(data) != size:
        raise ValueError(
            f"Could not read {size} bytes at offset {offset} from {source}; "
            f"got {len(data)} bytes. File may be too small."
        )
    return data


def extract_normal_volume_header(source: Path) -> ExtractionCandidate:
    """Extract the 512-byte normal volume header (offset 0)."""
    _open_source_readonly(source)
    data = _read_slice(source, OFFSET_NORMAL_VOLUME, HEADER_SIZE)
    sha256 = hashlib.sha256(data).hexdigest()
    return ExtractionCandidate(
        candidate_type="normal_volume_header",
        offset=OFFSET_NORMAL_VOLUME,
        data=data,
        sha256=sha256,
    )


def extract_hidden_volume_header(source: Path) -> ExtractionCandidate:
    """Extract the 512-byte hidden volume header (offset 65536)."""
    _open_source_readonly(source)
    data = _read_slice(source, OFFSET_HIDDEN_VOLUME, HEADER_SIZE)
    sha256 = hashlib.sha256(data).hexdigest()
    return ExtractionCandidate(
        candidate_type="hidden_volume_header",
        offset=OFFSET_HIDDEN_VOLUME,
        data=data,
        sha256=sha256,
    )


def extract_normal_system_header(source: Path) -> ExtractionCandidate:
    """Extract the 512-byte normal system header (offset 31744)."""
    _open_source_readonly(source)
    data = _read_slice(source, OFFSET_NORMAL_SYSTEM, HEADER_SIZE)
    sha256 = hashlib.sha256(data).hexdigest()
    return ExtractionCandidate(
        candidate_type="normal_system_header",
        offset=OFFSET_NORMAL_SYSTEM,
        data=data,
        sha256=sha256,
    )


def extract_candidates(
    source: Path,
    include_normal: bool = True,
    include_hidden: bool = True,
    include_system: bool = False,
) -> list[ExtractionCandidate]:
    """Extract selected 512-byte header candidates from a container.

    Parameters
    ----------
    source:
        Path to a VeraCrypt/TrueCrypt file container or disk image.
        Never modified.
    include_normal:
        Extract the normal volume header at offset 0.
    include_hidden:
        Extract the hidden volume header at offset 65536.
    include_system:
        Extract the system header at offset 31744 (for system-encrypted drives).
    """
    _open_source_readonly(source)
    candidates: list[ExtractionCandidate] = []

    if include_normal:
        try:
            candidates.append(extract_normal_volume_header(source))
        except ValueError:
            pass  # file too small for this candidate

    if include_hidden:
        try:
            candidates.append(extract_hidden_volume_header(source))
        except ValueError:
            pass

    if include_system:
        try:
            candidates.append(extract_normal_system_header(source))
        except ValueError:
            pass

    return candidates
