"""DiagnosticBundle metadata model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiagnosticBundle:
    """Metadata for an exported diagnostic bundle zip."""

    bundle_id: str
    created_timestamp: str
    workspace_id: str
    app_version: str
    os_summary: str
    hashcat_version: str | None
    schema_version: int
    included_files: list[str] = field(default_factory=list)
    excluded_categories: list[str] = field(default_factory=list)
    bundle_path: str = ""  # workspace-relative path to zip

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "bundle_id": self.bundle_id,
            "created_timestamp": self.created_timestamp,
            "workspace_id": self.workspace_id,
            "app_version": self.app_version,
            "os_summary": self.os_summary,
            "hashcat_version": self.hashcat_version,
            "included_files": self.included_files,
            "excluded_categories": self.excluded_categories,
            "bundle_path": self.bundle_path,
        }
