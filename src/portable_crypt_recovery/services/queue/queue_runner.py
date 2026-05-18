"""Queue runner: runs jobs one at a time using the process runner."""

from __future__ import annotations

import contextlib
import threading
import time
from collections.abc import Callable
from pathlib import Path

from portable_crypt_recovery.core.atomic_write import atomic_write_json
from portable_crypt_recovery.core.timestamps import utc_now_iso
from portable_crypt_recovery.models.job import QueuedJob
from portable_crypt_recovery.models.queue_state import QueueState
from portable_crypt_recovery.services.hashcat.process_runner import HashcatProcessRunner
from portable_crypt_recovery.services.queue.result_classifier import classify_result
from portable_crypt_recovery.services.queue.runner_lock import acquire_lock, release_lock

_EXIT_MEANINGS: dict[int | None, str] = {
    0: "CRACKED",
    1: "EXHAUSTED — all candidates tried, no match",
    2: "ABORTED — user or runtime stopped job",
    3: "ABORTED_CHECKPOINT",
    4: "ABORTED_RUNTIME",
    5: "ABORTED_FINISH",
    4294967295: "ERROR (-1) — hashcat internal error",
}


def _summarize_hardware_flags(args: list[str], stored_mode: int | None = None) -> str:
    """Extract key hardware flags from a hashcat command array into a readable line.

    Reads the already-built command array so the log reflects what was actually
    passed to hashcat (not what settings claimed to be set at the time).
    stored_mode: the mode number recorded in the job (before any substitution).
    """
    cuda_ignored = "--backend-ignore-cuda" in args

    cpu_opencl = False
    if "-D" in args:
        idx = args.index("-D")
        if idx + 1 < len(args):
            cpu_opencl = args[idx + 1] == "1"

    optimized = "-O" in args
    hwmon_off = "--hwmon-disable" in args
    logfile_off = "--logfile-disable" in args

    devices = "all"
    if "-d" in args:
        idx = args.index("-d")
        if idx + 1 < len(args):
            devices = args[idx + 1]

    # Detect mode substitution: job stores original mode; command may use legacy
    cmd_mode: int | None = None
    if "-m" in args:
        idx = args.index("-m")
        if idx + 1 < len(args):
            with contextlib.suppress(ValueError):
                cmd_mode = int(args[idx + 1])
    mode_note = ""
    if stored_mode is not None and cmd_mode is not None and cmd_mode != stored_mode:
        mode_note = (
            f"  |  mode_substituted={stored_mode}→{cmd_mode}"
            " (legacy GPU kernel, no CPU bridge)"
        )

    parts = [
        f"CUDA={'ignored (--backend-ignore-cuda)' if cuda_ignored else 'enabled'}",
        f"cpu_opencl={'yes (-D 1)' if cpu_opencl else 'no'}",
        f"devices={devices}",
        f"opt_kernels={'yes (-O)' if optimized else 'no'}",
        f"hwmon={'off' if hwmon_off else 'on'}",
        f"logfile={'off' if logfile_off else 'on'}",
    ]
    return "  |  ".join(parts) + mode_note


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
        self._stop_requeue = False   # True → reset job to pending instead of failed
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
        """Terminate current job and reset it to pending so it re-runs next time."""
        self._stop_discard = False
        self._stop_requeue = True
        self._stop_after_current = True   # also stop the loop after this job
        with self._lock:
            if self._current_runner:
                self._current_runner.terminate()

    def stop_and_discard(self) -> None:
        """Terminate current job and mark it as failed (will not re-run)."""
        self._stop_discard = True
        self._stop_requeue = False
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
                job_after = self._queue_state.jobs.get(job_id)
                if job_after is not None and job_after.status == "cracked":
                    if self._behavior_after_crack == "stop_entire_queue":
                        # Stop the whole queue immediately.
                        break
                    else:
                        # "continue_other_uncracked_targets": skip every other
                        # pending job that targets the same header — they are
                        # redundant now that the header is cracked.  Jobs for
                        # different headers are left pending so they still run.
                        cracked_header = job_after.header_id
                        for other_jid in self._queue_state.queue_order:
                            other = self._queue_state.jobs.get(other_jid)
                            if (
                                other is not None
                                and other.status == "pending"
                                and other.header_id == cracked_header
                            ):
                                other.status = "skipped"
                                other.updated_timestamp = utc_now_iso()
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

        try:
            self._run_job_inner(job)
        except Exception as exc:
            # Safety net: never leave a job stuck as "running" if something
            # unexpected throws (bad path, file lock, OS error, etc.).
            job.status = "failed"
            job.updated_timestamp = utc_now_iso()
            # Best-effort: append the exception to the log so the user can see why
            try:
                log_path = self._workspace_root / job.log_path
                log_path.parent.mkdir(parents=True, exist_ok=True)
                with log_path.open("a", encoding="utf-8") as fh:
                    fh.write(
                        f"\n=== PCR INTERNAL ERROR ===\n"
                        f"exception   : {type(exc).__name__}: {exc}\n"
                        f"=========================\n"
                    )
            except OSError:
                pass
        finally:
            self._queue_state.current_running_job = None
            self._save_queue_state()
            if self._on_status_update:
                self._on_status_update(self._queue_state)

    def _run_job_inner(self, job: QueuedJob) -> None:
        """Core job execution logic; called inside a try/except by _run_job."""
        log_path = self._workspace_root / job.log_path
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Use existing command_array if set, otherwise it's empty.
        # Write the log header FIRST so the log always has some content,
        # even if the command array is empty or hashcat exits immediately.
        args = job.command_array
        start_ts = utc_now_iso()
        start_mono = time.monotonic()
        hardware_summary = (
            _summarize_hardware_flags(args, stored_mode=job.hashcat_mode)
            if args else "(no command)"
        )
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(
                f"=== PCR JOB START ===\n"
                f"job_id      : {job.job_id}\n"
                f"mode        : {job.hashcat_mode}\n"
                f"session     : {job.session_name}\n"
                f"started     : {start_ts}\n"
                f"hardware    : {hardware_summary}\n"
                f"command     : {' '.join(args) if args else '(none — command array was empty)'}\n"
                f"outfile     : {self._workspace_root / job.outfile_path}\n"
                f"potfile     : {self._workspace_root / job.potfile_path}\n"
                f"=== HASHCAT OUTPUT BELOW ===\n"
            )

        if not args:
            # No command was built for this job — mark failed and write the
            # reason to the log so the user can see why it didn't run.
            with log_path.open("a", encoding="utf-8") as fh:
                fh.write(
                    "\n[ERROR] command_array is empty.\n"
                    "This usually means command building failed at queue start.\n"
                    "Check that the header file, wordlist, and hashcat path all exist,\n"
                    "then restart the queue to rebuild commands.\n"
                )
            job.status = "failed"
            return

        # cwd MUST be the directory containing hashcat.exe so that hashcat can
        # resolve ./OpenCL/, ./modules/, and other relative data paths it ships
        # with.  Using a workspace sub-folder as CWD causes immediate exit with
        # "./OpenCL/: No such file or directory".
        hashcat_exe_dir = self._hashcat_exe.parent

        # Keep OS-level temp writes inside the portable workspace so no
        # artefacts end up in the user profile or system TEMP.
        ws_hashcat = self._workspace_root / "hashcat"
        tmp_dir = ws_hashcat / "tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)

        extra_env: dict[str, str] = {
            "TEMP": str(tmp_dir),
            "TMP": str(tmp_dir),
            "TMPDIR": str(tmp_dir),
        }

        with self._lock:
            self._current_runner = HashcatProcessRunner(
                args=args,
                log_path=log_path,
                cwd=hashcat_exe_dir,
                extra_env=extra_env,
            )
            self._current_runner.start()

        exit_code = self._current_runner.wait()
        stdout_lines = self._current_runner.get_result().stdout_lines

        with self._lock:
            self._current_runner = None

        # Classify result — save raw crack BEFORE any report generation
        outfile = self._workspace_root / job.outfile_path
        potfile = self._workspace_root / job.potfile_path
        classification = classify_result(exit_code, outfile, potfile)

        if self._stop_requeue:
            # stop_and_save: reset to pending so the job reruns next queue start
            job.status = "pending"
            job.cracked_password = None
        elif self._stop_discard:
            job.status = "failed"
        else:
            job.status = classification.status
            if classification.cracked_password:
                job.cracked_password = classification.cracked_password

        # Write footer — always include exit code so failed jobs are diagnosable.
        end_ts = utc_now_iso()
        elapsed_s = time.monotonic() - start_mono
        exit_meaning = _EXIT_MEANINGS.get(exit_code, f"unknown ({exit_code})")
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write("\n=== PCR JOB END ===\n")
            fh.write(f"finished    : {end_ts}\n")
            fh.write(f"elapsed     : {elapsed_s:.2f}s\n")
            fh.write(f"exit_code   : {exit_code}  ({exit_meaning})\n")
            fh.write(f"result      : {job.status}\n")
            fh.write(f"hardware    : {hardware_summary}\n")
            # Warn when hashcat produced zero output and the exit code is an error
            if not stdout_lines and exit_code not in (0, 1, 2, 3, 4, 5):
                fh.write(
                    "\n[WARNING] Hashcat produced no output before exiting.\n"
                    "Possible causes:\n"
                    "  - CUDA PTX version mismatch (try enabling 'Ignore CUDA' in Settings)\n"
                    "  - Hash mode module not present in this hashcat build\n"
                    "  - Unsupported flag for this hashcat version\n"
                    "  - OpenCL / CUDA driver missing or incompatible\n"
                    "  - Header file path could not be resolved\n"
                    f"Command was: {' '.join(args)}\n"
                )
            if job.cracked_password:
                fh.write(f"PASSWORD    : {job.cracked_password}\n")
            fh.write("===================\n")

        job.updated_timestamp = utc_now_iso()

    def _save_queue_state(self) -> None:
        path = self._workspace_root / "queue" / "queue-state.json"
        atomic_write_json(path, self._queue_state.to_dict())
