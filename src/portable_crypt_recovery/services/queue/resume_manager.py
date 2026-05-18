"""Resume manager: check for stopped jobs that can be resumed."""

from __future__ import annotations

from pathlib import Path

from portable_crypt_recovery.models.queue_state import QueueState
from portable_crypt_recovery.models.task import QueuedTask


def find_resumable_job(queue_state: QueueState, workspace_root: Path) -> QueuedTask | None:
    """Return the first task with status 'stopped_saved' that has a restore file.

    Returns None if no resumable task is found.
    """
    for task_id in queue_state.task_order:
        task = queue_state.tasks.get(task_id)
        if task is None:
            continue
        if task.status != "stopped_saved":
            continue
        restore_file = workspace_root / "hashcat" / "restore" / f"{task.session_name}.restore"
        if restore_file.exists():
            return task
    return None


def build_resume_args(
    hashcat_executable: Path,
    session_name: str,
) -> list[str]:
    """Build a Hashcat --restore argument array for a saved session.

    Returns list[str] — safe for subprocess.Popen with list args.
    """
    return [
        str(hashcat_executable.resolve()),
        "--session", session_name,
        "--restore",
    ]
