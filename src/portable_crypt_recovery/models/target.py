"""Target model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Target:
    """Represents a VeraCrypt or TrueCrypt volume target."""

    target_id: str
    display_name: str
    original_path: str  # workspace-relative or absolute path to source
    source_type: str  # "file_container" | "disk_image" | "extracted_header" | "unknown"
    container_family: str  # "veracrypt" | "truecrypt" | "unknown"
    ownership_confirmed: bool = False
    notes: str = ""
    created_timestamp: str = ""
    updated_timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "target_id": self.target_id,
            "display_name": self.display_name,
            "original_path": self.original_path,
            "source_type": self.source_type,
            "container_family": self.container_family,
            "ownership_confirmed": self.ownership_confirmed,
            "notes": self.notes,
            "created_timestamp": self.created_timestamp,
            "updated_timestamp": self.updated_timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Target:
        return cls(
            target_id=data["target_id"],
            display_name=data["display_name"],
            original_path=data["original_path"],
            source_type=data.get("source_type", "unknown"),
            container_family=data.get("container_family", "unknown"),
            ownership_confirmed=data.get("ownership_confirmed", False),
            notes=data.get("notes", ""),
            created_timestamp=data.get("created_timestamp", ""),
            updated_timestamp=data.get("updated_timestamp", ""),
        )
