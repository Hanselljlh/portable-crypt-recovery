"""KeyfileSet and KeyfileEntry models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class KeyfileEntry:
    """A single normalized keyfile entry."""

    keyfile_id: str
    original_path: str
    normalized_workspace_path: str  # workspace-relative
    size_bytes: int
    sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "keyfile_id": self.keyfile_id,
            "original_path": self.original_path,
            "normalized_workspace_path": self.normalized_workspace_path,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KeyfileEntry":
        return cls(
            keyfile_id=data["keyfile_id"],
            original_path=data.get("original_path", ""),
            normalized_workspace_path=data["normalized_workspace_path"],
            size_bytes=data.get("size_bytes", 0),
            sha256=data.get("sha256", ""),
        )


@dataclass
class KeyfileSet:
    """A set of keyfiles used together in a Hashcat job."""

    set_id: str
    entries: list[KeyfileEntry] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "set_id": self.set_id,
            "entries": [e.to_dict() for e in self.entries],
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KeyfileSet":
        entries = [KeyfileEntry.from_dict(e) for e in data.get("entries", [])]
        return cls(
            set_id=data["set_id"],
            entries=entries,
            notes=data.get("notes", ""),
        )
