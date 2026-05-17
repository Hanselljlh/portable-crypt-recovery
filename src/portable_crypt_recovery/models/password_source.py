"""PasswordSource model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PasswordSource:
    """A password list or generation recipe for Hashcat jobs."""

    source_id: str
    source_type: str  # "wordlist" | "generated" | "manual"
    workspace_relative_path: str | None = None  # for wordlists
    is_external: bool = False
    candidate_count: int = 0
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "source_id": self.source_id,
            "source_type": self.source_type,
            "workspace_relative_path": self.workspace_relative_path,
            "is_external": self.is_external,
            "candidate_count": self.candidate_count,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PasswordSource":
        return cls(
            source_id=data["source_id"],
            source_type=data.get("source_type", "wordlist"),
            workspace_relative_path=data.get("workspace_relative_path"),
            is_external=data.get("is_external", False),
            candidate_count=data.get("candidate_count", 0),
            notes=data.get("notes", ""),
        )
