"""Tests for the job→task queue-state schema migration (0.1.29).

Covers:
- workspace_schema emits new canonical keys
- QueueState.from_dict reads new-key files
- QueueState.from_dict falls back to old-key files (legacy compat)
- startup task-count reads new-key files correctly
- startup task-count falls back to old-key files
- workspace_summary counts tasks from new-key files
- workspace_summary counts tasks from old-key files (legacy compat)
"""

from __future__ import annotations

import json

from portable_crypt_recovery.models.queue_state import QueueState
from portable_crypt_recovery.services.diagnostics.workspace_summary import (
    generate_workspace_summary,
)
from portable_crypt_recovery.workspace.workspace_schema import empty_queue_state_record

# ---------------------------------------------------------------------------
# workspace_schema
# ---------------------------------------------------------------------------

def test_empty_queue_state_record_uses_new_keys():
    rec = empty_queue_state_record()
    assert "tasks" in rec, "must use 'tasks' key"
    assert "task_order" in rec, "must use 'task_order' key"
    assert "current_running_task" in rec, "must use 'current_running_task' key"
    # old keys must be absent
    assert "jobs" not in rec
    assert "queue_order" not in rec
    assert "current_running_job" not in rec


# ---------------------------------------------------------------------------
# QueueState.from_dict — new keys
# ---------------------------------------------------------------------------

def test_queue_state_from_dict_new_keys():
    data = {
        "schema_version": 1,
        "task_order": ["t1", "t2"],
        "current_running_task": "t1",
        "status": "running",
        "tasks": {},   # empty — no QueuedTask construction needed
    }
    qs = QueueState.from_dict(data)
    assert qs.task_order == ["t1", "t2"]
    assert qs.current_running_task == "t1"
    assert qs.status == "running"


# ---------------------------------------------------------------------------
# QueueState.from_dict — legacy keys (backward compat)
# ---------------------------------------------------------------------------

def test_queue_state_from_dict_legacy_keys():
    data = {
        "schema_version": 1,
        "queue_order": ["j1", "j2"],
        "current_running_job": "j1",
        "status": "stopped",
        "jobs": {},
    }
    qs = QueueState.from_dict(data)
    assert qs.task_order == ["j1", "j2"], "should fall back to queue_order"
    assert qs.current_running_task == "j1", "should fall back to current_running_job"
    assert qs.status == "stopped"


def test_queue_state_from_dict_new_keys_take_priority():
    """When both old and new keys are present, new keys win."""
    data = {
        "schema_version": 1,
        "task_order": ["new1"],
        "queue_order": ["old1"],
        "current_running_task": "new1",
        "current_running_job": "old1",
        "status": "stopped",
        "tasks": {},
        "jobs": {},
    }
    qs = QueueState.from_dict(data)
    assert qs.task_order == ["new1"]
    assert qs.current_running_task == "new1"


# ---------------------------------------------------------------------------
# startup task-count reading
# ---------------------------------------------------------------------------

def _write_queue_file(ws_root, payload: dict) -> None:
    queue_dir = ws_root / "queue"
    queue_dir.mkdir(parents=True, exist_ok=True)
    (queue_dir / "queue-state.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )


def _count_tasks_from_queue(ws_root) -> int:
    """Mirror the logic in startup.try_auto_open_workspace."""
    queue_file = ws_root / "queue" / "queue-state.json"
    if not queue_file.exists():
        return 0
    qs_data = json.loads(queue_file.read_text(encoding="utf-8"))
    tasks_map = qs_data["tasks"] if "tasks" in qs_data else qs_data.get("jobs", {})
    return len(tasks_map)


def test_startup_task_count_new_schema(tmp_path):
    _write_queue_file(tmp_path, {
        "schema_version": 1, "task_order": ["a", "b"], "tasks": {"a": {}, "b": {}},
        "status": "stopped", "current_running_task": None,
    })
    assert _count_tasks_from_queue(tmp_path) == 2


def test_startup_task_count_legacy_schema(tmp_path):
    _write_queue_file(tmp_path, {
        "schema_version": 1, "queue_order": ["x"], "jobs": {"x": {}},
        "status": "stopped", "current_running_job": None,
    })
    assert _count_tasks_from_queue(tmp_path) == 1


def test_startup_task_count_missing_file(tmp_path):
    assert _count_tasks_from_queue(tmp_path) == 0


# ---------------------------------------------------------------------------
# workspace_summary
# ---------------------------------------------------------------------------

def _make_minimal_workspace(ws_root) -> None:
    ws_root.mkdir(parents=True, exist_ok=True)
    (ws_root / "workspace.json").write_text(
        json.dumps({
            "workspace_id": "w1", "workspace_name": "test",
            "created_timestamp": "2024-01-01T00:00:00Z",
            "app_version": "0.1.29",
        }),
        encoding="utf-8",
    )


def test_workspace_summary_task_count_new_schema(tmp_path):
    ws = tmp_path / "ws"
    _make_minimal_workspace(ws)
    _write_queue_file(ws, {
        "schema_version": 1, "task_order": ["a", "b", "c"],
        "tasks": {"a": {}, "b": {}, "c": {}},
        "status": "stopped", "current_running_task": None,
    })
    summary = generate_workspace_summary(ws)
    assert "Tasks:   3" in summary


def test_workspace_summary_task_count_legacy_schema(tmp_path):
    ws = tmp_path / "ws"
    _make_minimal_workspace(ws)
    _write_queue_file(ws, {
        "schema_version": 1, "queue_order": ["x", "y"],
        "jobs": {"x": {}, "y": {}},
        "status": "stopped", "current_running_job": None,
    })
    summary = generate_workspace_summary(ws)
    assert "Tasks:   2" in summary


def test_workspace_summary_task_count_no_queue(tmp_path):
    ws = tmp_path / "ws"
    _make_minimal_workspace(ws)
    summary = generate_workspace_summary(ws)
    assert "Tasks:   0" in summary
