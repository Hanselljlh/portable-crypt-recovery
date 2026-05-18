"""Task models (individual hashcat invocations)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

JOB_STATUSES = (
    "pending",
    "running",
    "paused",
    "stopped_saved",
    "cracked",
    "exhausted",
    "failed",
    "skipped",
)


@dataclass
class JobDraft:
    """Incomplete job configuration before expansion."""

    draft_id: str
    target_id: str
    header_id: str
    hash_mode_set_id: str
    pim_set_id: str | None
    keyfile_set_id: str | None
    password_source_id: str
    notes: str = ""
    created_timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "draft_id": self.draft_id,
            "target_id": self.target_id,
            "header_id": self.header_id,
            "hash_mode_set_id": self.hash_mode_set_id,
            "pim_set_id": self.pim_set_id,
            "keyfile_set_id": self.keyfile_set_id,
            "password_source_id": self.password_source_id,
            "notes": self.notes,
            "created_timestamp": self.created_timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JobDraft:
        return cls(
            draft_id=data["draft_id"],
            target_id=data["target_id"],
            header_id=data["header_id"],
            hash_mode_set_id=data["hash_mode_set_id"],
            pim_set_id=data.get("pim_set_id"),
            keyfile_set_id=data.get("keyfile_set_id"),
            password_source_id=data["password_source_id"],
            notes=data.get("notes", ""),
            created_timestamp=data.get("created_timestamp", ""),
        )


@dataclass
class QueuedTask:
    """A fully expanded, ready-to-run Hashcat task (individual hashcat invocation)."""

    task_id: str
    target_id: str
    header_id: str
    hash_mode_set_id: str
    pim_set_id: str | None
    keyfile_set_id: str | None
    password_source_id: str
    status: str  # one of JOB_STATUSES
    command_array: list[str]  # never a shell string
    potfile_path: str  # workspace-relative
    outfile_path: str  # workspace-relative
    log_path: str  # workspace-relative
    session_name: str
    hashcat_mode: int = 0
    pim_value: int | None = None
    pim_mode: str = "default"  # "default" | "custom"
    wordlist_path: str = ""  # abs path or workspace-relative; empty = no wordlist arg
    created_timestamp: str = ""
    updated_timestamp: str = ""
    notes: str = ""
    # Draft provenance — which draft this task was expanded from
    draft_id: str = ""
    draft_label: str = ""
    # Crack result — populated by queue runner after classification
    cracked_password: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "task_id": self.task_id,
            "target_id": self.target_id,
            "header_id": self.header_id,
            "hash_mode_set_id": self.hash_mode_set_id,
            "pim_set_id": self.pim_set_id,
            "keyfile_set_id": self.keyfile_set_id,
            "password_source_id": self.password_source_id,
            "status": self.status,
            "command_array": self.command_array,
            "potfile_path": self.potfile_path,
            "outfile_path": self.outfile_path,
            "log_path": self.log_path,
            "session_name": self.session_name,
            "hashcat_mode": self.hashcat_mode,
            "pim_value": self.pim_value,
            "pim_mode": self.pim_mode,
            "wordlist_path": self.wordlist_path,
            "created_timestamp": self.created_timestamp,
            "updated_timestamp": self.updated_timestamp,
            "notes": self.notes,
            "draft_id": self.draft_id,
            "draft_label": self.draft_label,
            "cracked_password": self.cracked_password,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QueuedTask:
        return cls(
            task_id=data["task_id"],
            target_id=data["target_id"],
            header_id=data["header_id"],
            hash_mode_set_id=data["hash_mode_set_id"],
            pim_set_id=data.get("pim_set_id"),
            keyfile_set_id=data.get("keyfile_set_id"),
            password_source_id=data["password_source_id"],
            status=data.get("status", "pending"),
            command_array=data.get("command_array", []),
            potfile_path=data.get("potfile_path", ""),
            outfile_path=data.get("outfile_path", ""),
            log_path=data.get("log_path", ""),
            session_name=data.get("session_name", ""),
            hashcat_mode=data.get("hashcat_mode", 0),
            pim_value=data.get("pim_value"),
            pim_mode=data.get("pim_mode", "default"),
            wordlist_path=data.get("wordlist_path", ""),
            created_timestamp=data.get("created_timestamp", ""),
            updated_timestamp=data.get("updated_timestamp", ""),
            notes=data.get("notes", ""),
            draft_id=data.get("draft_id", ""),
            draft_label=data.get("draft_label", ""),
            cracked_password=data.get("cracked_password", ""),
        )
