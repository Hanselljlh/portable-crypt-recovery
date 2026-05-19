"""HashModeSet model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HashModeEntry:
    """A single Hashcat mode entry within a mode set."""

    mode: int
    label: str
    family: str  # "veracrypt" | "truecrypt"
    is_system: bool = False
    is_legacy: bool = False
    candidate_type: str = "normal_volume_header"
    # Cipher cascade level: 1 = single cipher (XTS 512), 2 = cascade ×2 (XTS 1024),
    # 3 = cascade ×3 (XTS 1536).  0 = unknown / not set.
    cipher_cascade: int = 0


@dataclass
class HashModeSet:
    """A collection of Hashcat modes for a target/header combination."""

    mode_set_id: str
    target_id: str = ""
    header_id: str = ""
    entries: list[HashModeEntry] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "mode_set_id": self.mode_set_id,
            "target_id": self.target_id,
            "header_id": self.header_id,
            "entries": [
                {
                    "mode": e.mode,
                    "label": e.label,
                    "family": e.family,
                    "is_system": e.is_system,
                    "is_legacy": e.is_legacy,
                    "candidate_type": e.candidate_type,
                    "cipher_cascade": e.cipher_cascade,
                }
                for e in self.entries
            ],
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HashModeSet:
        entries = [
            HashModeEntry(
                mode=e["mode"],
                label=e.get("label", ""),
                family=e.get("family", "unknown"),
                is_system=e.get("is_system", False),
                is_legacy=e.get("is_legacy", False),
                candidate_type=e.get("candidate_type", "normal_volume_header"),
                cipher_cascade=e.get("cipher_cascade", 0),
            )
            for e in data.get("entries", [])
        ]
        return cls(
            mode_set_id=data["mode_set_id"],
            target_id=data.get("target_id", ""),
            header_id=data.get("header_id", ""),
            entries=entries,
            notes=data.get("notes", ""),
        )
