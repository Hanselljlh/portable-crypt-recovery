"""Queue state model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from portable_crypt_recovery.models.job import QueuedJob

QUEUE_STATUSES = ("stopped", "running", "paused")


@dataclass
class QueueState:
    """In-memory representation of queue/queue-state.json."""

    queue_order: list[str] = field(default_factory=list)  # ordered job IDs
    current_running_job: str | None = None
    status: str = "stopped"
    jobs: dict[str, QueuedJob] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "queue_order": self.queue_order,
            "current_running_job": self.current_running_job,
            "status": self.status,
            "jobs": {jid: job.to_dict() for jid, job in self.jobs.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QueueState":
        jobs = {
            jid: QueuedJob.from_dict(jdata)
            for jid, jdata in data.get("jobs", {}).items()
        }
        return cls(
            queue_order=data.get("queue_order", []),
            current_running_job=data.get("current_running_job"),
            status=data.get("status", "stopped"),
            jobs=jobs,
        )
