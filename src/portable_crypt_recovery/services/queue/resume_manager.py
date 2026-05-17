"""Resume manager: check for stopped jobs that can be resumed."""

from __future__ import annotations

from pathlib import Path

from portable_crypt_recovery.models.job import QueuedJob
from portable_crypt_recovery.models.queue_state import QueueState


def find_resumable_job(queue_state: QueueState, workspace_root: Path) -> QueuedJob | None:
    """Return the first job with status 'stopped_saved' that has a restore file.

    Returns None if no resumable job is found.
    """
    for job_id in queue_state.queue_order:
        job = queue_state.jobs.get(job_id)
        if job is None:
            continue
        if job.status != "stopped_saved":
            continue
        restore_file = workspace_root / "hashcat" / "restore" / f"{job.session_name}.restore"
        if restore_file.exists():
            return job
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
