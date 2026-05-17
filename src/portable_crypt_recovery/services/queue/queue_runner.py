"""Queue runner: runs jobs one at a time using the process runner."""

from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import Path

from portable_crypt_recovery.core.atomic_write import atomic_write_json
from portable_crypt_recovery.core.timestamps import utc_now_iso
from portable_crypt_recovery.models.job import QueuedJob
from portable_crypt_recovery.models.queue_state import QueueState
from portable_crypt_recovery.services.hashcat.process_runner import HashcatProcessRunner
from portable_crypt_recovery.services.queue.result_classifier import classify_result
from portable_crypt_recovery.services.queue.runner_lock import acquire_lock, release_lock


class QueueRunner:
    """Runs queued jobs one at a time.

    Parameters
    ----------
    workspace_root:
        Workspace root directory.
    queue_state:
        Mutable queue state object (modified in place).
    hashcat_executable:
        Path to the Hashcat binary.
    on_status_update:
        Optional callback after each job completes or status changes.
    """

    def __init__(
        self,
        workspace_root: Path,
        queue_state: QueueState,
        hashcat_executable: Path,
        on_status_update: Callable[[QueueState], None] | None = None,
        behavior_after_crack: str = "continue_other_uncracked_targets",
    ) -> None:
        self._workspace_root = workspace_root
        self._queue_state = queue_state
        self._hashcat_exe = hashcat_executable
        self._on_status_update = on_status_update
        self._behavior_after_crack = behavior_after_crack
        self._current_runner: HashcatProcessRunner | None = None
        self._stop_after_current = False
        self._stop_discard = False
        self._lock = threading.Lock()

    def start(self) -> bool:
        """Start the queue in a background thread. Returns False if already locked."""
        if not acquire_lock(self._workspace_root):
            return False
        self._queue_state.status = "running"
        self._save_queue_state()
        t = threading.Thread(target=self._run_loop, daemon=True)
        t.start()
        return True

    def pause(self) -> None:
        """Suspend the current job process."""
        with self._lock:
            if self._current_runner:
                self._current_runner.pause()
        self._queue_state.status = "paused"
        self._save_queue_state()

    def resume(self) -> None:
        """Resume a paused job process."""
        with self._lock:
            if self._current_runner:
                self._current_runner.resume()
        self._queue_state.status = "running"
        self._save_queue_state()

    def stop_after_current(self) -> None:
        """Signal the runner to stop after the current job finishes."""
        self._stop_after_current = True

    def stop_and_save(self) -> None:
        """Terminate current job and mark it as stopped_saved."""
        self._stop_discard = False
        with self._lock:
            if self._current_runner:
                self._current_runner.terminate()

    def stop_and_discard(self) -> None:
        """Terminate current job and mark it as failed."""
        self._stop_discard = True
        with self._lock:
            if self._current_runner:
                self._current_runner.terminate()

    def _run_loop(self) -> None:
        try:
            for job_id in list(self._queue_state.queue_order):
                if self._stop_after_current:
                    break
                job = self._queue_state.jobs.get(job_id)
                if job is None or job.status != "pending":
                    continue
                self._run_job(job)
                if self._stop_after_current:
                    break
                # Stop entire queue when any job cracks (if configured)
                job_after = self._queue_state.jobs.get(job_id)
                if (
                    job_after is not None
                    and job_after.status == "cracked"
                    and self._behavior_after_crack == "stop_entire_queue"
                ):
                    break
        finally:
            self._queue_state.status = "stopped"
            self._queue_state.current_running_job = None
            self._save_queue_state()
            release_lock(self._workspace_root)
            if self._on_status_update:
                self._on_status_update(self._queue_state)

    def _run_job(self, job: QueuedJob) -> None:
        job.status = "running"
        job.updated_timestamp = utc_now_iso()
        self._queue_state.current_running_job = job.job_id
        self._save_queue_state()

        # Use existing command_array if set, otherwise it's empty
        args = job.command_array
        if not args:
            job.status = "failed"
            job.updated_timestamp = utc_now_iso()
            self._save_queue_state()
            return

        log_path = self._workspace_root / job.log_path

        with self._lock:
            self._current_runner = HashcatProcessRunner(args=args, log_path=log_path)
            self._current_runner.start()

        exit_code = self._current_runner.wait()

        with self._lock:
            self._current_runner = None

        # Classify result — save raw crack BEFORE any report generation
        outfile = self._workspace_root / job.outfile_path
        potfile = self._workspace_root / job.potfile_path
        classification = classify_result(exit_code, outfile, potfile)

        if self._stop_discard:
            job.status = "failed"
        else:
            job.status = classification.status

        job.updated_timestamp = utc_now_iso()
        self._queue_state.current_running_job = None
        self._save_queue_state()

        if self._on_status_update:
            self._on_status_update(self._queue_state)

    def _save_queue_state(self) -> None:
        path = self._workspace_root / "queue" / "queue-state.json"
        atomic_write_json(path, self._queue_state.to_dict())
