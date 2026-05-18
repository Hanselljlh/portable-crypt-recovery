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
        tasks = {
            tid: QueuedTask.from_dict(tdata)
            for tid, tdata in data.get("tasks", {}).items()
        }
        return cls(
            task_order=data.get("task_order", []),
            current_running_task=data.get("current_running_task"),
            status=data.get("status", "stopped"),
            tasks=tasks,
        )
