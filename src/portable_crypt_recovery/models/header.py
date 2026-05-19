"""Header model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

HEADER_SIZE_BYTES = 512


@dataclass
class Header:
    """Represents an extracted or imported 512-byte volume header."""

    header_id: str
    target_id: str
    source_type: str  # "extracted" | "imported"
    workspace_relative_path: str  # relative path inside workspace
    size_bytes: int
    sha256: str
    extraction_timestamp: str
    # "normal_volume_header" | "hidden_volume_header" | "normal_system_header"
    # | "hidden_system_candidate" | "unknown_imported_header"
    candidate_type: str = "unknown"
    notes: str = ""
    # Optional recovery hints — narrow down which Hashcat modes are tried.
    # Empty list = no filter = try all.  Values: "sha512" "ripemd160" "sha256"
    # "whirlpool" "streebog512"
    known_kdfs: list = field(default_factory=list)
    # Empty list = try all.  Values: 512 1024 1536  (XTS key size in bits)
    known_xts_sizes: list = field(default_factory=list)

    def validate_size(self) -> None:
        """Raise ValueError if header is not exactly 512 bytes."""
        if self.size_bytes != HEADER_SIZE_BYTES:
            raise ValueError(
                f"Header must be exactly {HEADER_SIZE_BYTES} bytes, got {self.size_bytes}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "header_id": self.header_id,
            "target_id": self.target_id,
            "source_type": self.source_type,
            "workspace_relative_path": self.workspace_relative_path,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "extraction_timestamp": self.extraction_timestamp,
            "candidate_type": self.candidate_type,
            "notes": self.notes,
            "known_kdfs": self.known_kdfs,
            "known_xts_sizes": self.known_xts_sizes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Header:
        return cls(
            header_id=data["header_id"],
            target_id=data["target_id"],
            source_type=data.get("source_type", "extracted"),
            workspace_relative_path=data["workspace_relative_path"],
            size_bytes=data["size_bytes"],
            sha256=data["sha256"],
            extraction_timestamp=data.get("extraction_timestamp", ""),
            candidate_type=data.get("candidate_type", "unknown"),
            notes=data.get("notes", ""),
            known_kdfs=data.get("known_kdfs", []),
            known_xts_sizes=data.get("known_xts_sizes", []),
        )
