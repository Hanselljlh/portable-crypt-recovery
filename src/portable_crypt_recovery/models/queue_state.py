"""Queue state model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from portable_crypt_recovery.models.task import QueuedTask

QUEUE_STATUSES = ("stopped", "running", "paused")


@dataclass
class QueueState:
    """In-memory representation of queue/queue-state.json."""

    task_order: list[str] = field(default_factory=list)  # ordered task IDs
    current_running_task: str | None = None
    status: str = "stopped"
    tasks: dict[str, QueuedTask] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "task_order": self.task_order,
            "current_running_task": self.current_running_task,
            "status": self.status,
            "tasks": {tid: task.to_dict() for tid, task in self.tasks.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QueueState:
        # Support queue-state files written before the job→task rename (< 0.1.29).
        # Prefer new keys; fall back to old keys only when the new key is absent.
        tasks_raw = data["tasks"] if "tasks" in data else data.get("jobs", {})
        task_order = data["task_order"] if "task_order" in data else data.get("queue_order", [])
        current_running_task = (
            data["current_running_task"]
            if "current_running_task" in data
            else data.get("current_running_job")
        )
        tasks = {
            tid: QueuedTask.from_dict(tdata)
            for tid, tdata in tasks_raw.items()
        }
        return cls(
            task_order=task_order,
            current_running_task=current_running_task,
            status=data.get("status", "stopped"),
            tasks=tasks,
        )
