"""Report model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Report:
    """Metadata for a cracked-job report."""

    report_id: str
    job_id: str
    cracked_password: str | None = None  # None if not cracked
    recovered_header_path: str = ""  # workspace-relative path to normalized header
    command_used: list[str] = field(default_factory=list)
    stats_text: str = ""
    created_timestamp: str = ""
    report_folder: str = ""  # workspace-relative path to report folder

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "report_id": self.report_id,
            "job_id": self.job_id,
            "cracked_password": self.cracked_password,
            "recovered_header_path": self.recovered_header_path,
            "command_used": self.command_used,
            "stats_text": self.stats_text,
            "created_timestamp": self.created_timestamp,
            "report_folder": self.report_folder,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Report":
        return cls(
            report_id=data["report_id"],
            job_id=data["job_id"],
            cracked_password=data.get("cracked_password"),
            recovered_header_path=data.get("recovered_header_path", ""),
            command_used=data.get("command_used", []),
            stats_text=data.get("stats_text", ""),
            created_timestamp=data.get("created_timestamp", ""),
            report_folder=data.get("report_folder", ""),
        )
