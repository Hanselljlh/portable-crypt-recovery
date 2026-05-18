"""Hashcat process runner.

Runs Hashcat as a subprocess using argument arrays (subprocess.Popen with list).
Never uses shell=True or string concatenation.
Handles Windows (no SIGSTOP; CREATE_NO_WINDOW flag) and Linux differently.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RunnerResult:
    exit_code: int | None
    stdout_lines: list[str] = field(default_factory=list)
    error: str | None = None


class HashcatProcessRunner:
    """Run a single Hashcat job as a subprocess.

    Parameters
    ----------
    args:
        Full argument array including hashcat executable path at index 0.
    log_path:
        Path to write stdout output (in append mode).
    on_line:
        Optional callback called with each stdout line as it arrives.
    """

    def __init__(
        self,
        args: list[str],
        log_path: Path | None = None,
        on_line: Callable[[str], None] | None = None,
        cwd: Path | None = None,
        extra_env: dict[str, str] | None = None,
    ) -> None:
        if not args:
            raise ValueError("args must not be empty")
        self._args = args
        self._log_path = log_path
        self._on_line = on_line
        self._cwd = cwd
        self._extra_env = extra_env
        self._process: subprocess.Popen | None = None  # type: ignore[type-arg]
        self._lock = threading.Lock()
        self._stdout_lines: deque[str] = deque(maxlen=200)

    def start(self) -> None:
        """Start the Hashcat subprocess."""
        with self._lock:
            if self._process is not None:
                raise RuntimeError("Process already started.")

        # Build environment: inherit the full current env then apply overrides.
        # We never pass a *replacement* env so hashcat can still find its DLLs.
        merged_env = dict(os.environ)
        if self._extra_env:
            merged_env.update(self._extra_env)

        kwargs: dict = {
            "args": self._args,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
            "env": merged_env,
        }

        if self._cwd is not None:
            kwargs["cwd"] = str(self._cwd)

        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]

        log_fh = None
        if self._log_path:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            log_fh = self._log_path.open("a", encoding="utf-8")

        with self._lock:
            self._process = subprocess.Popen(**kwargs)  # type: ignore[call-overload]

        # Read stdout in a thread so we don't block
        def _reader() -> None:
            assert self._process is not None
            assert self._process.stdout is not None
            try:
                for line in self._process.stdout:
                    line = line.rstrip("\n")
                    self._stdout_lines.append(line)
                    if log_fh:
                        log_fh.write(line + "\n")
                        log_fh.flush()
                    if self._on_line:
                        self._on_line(line)
            finally:
                if log_fh:
                    log_fh.close()

        self._reader_thread = threading.Thread(target=_reader, daemon=True)
        self._reader_thread.start()

    def wait(self, timeout: float | None = None) -> int | None:
        """Wait for the process to finish. Returns exit code."""
        if self._process is None:
            raise RuntimeError("Process not started.")
        try:
            self._process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return None
        self._reader_thread.join(timeout=5.0)
        return self._process.returncode

    def pause(self) -> None:
        """Suspend the running process."""
        if self._process is None:
            return
        with self._lock:
            if self._process.poll() is not None:
                return
        if sys.platform == "win32":
            _windows_suspend(self._process.pid)
        else:
            import signal
            os.kill(self._process.pid, signal.SIGSTOP)

    def resume(self) -> None:
        """Resume a suspended process."""
        if self._process is None:
            return
        with self._lock:
            if self._process.poll() is not None:
                return
        if sys.platform == "win32":
            _windows_resume(self._process.pid)
        else:
            import signal
            os.kill(self._process.pid, signal.SIGCONT)

    def terminate(self) -> None:
        """Terminate the running process."""
        if self._process is None:
            return
        with self._lock:
            proc = self._process
        if proc.poll() is None:
            proc.terminate()

    def get_result(self) -> RunnerResult:
        if self._process is None:
            return RunnerResult(exit_code=None, error="Process not started.")
        return RunnerResult(
            exit_code=self._process.returncode,
            stdout_lines=list(self._stdout_lines),
        )


def _windows_suspend(pid: int) -> None:
    """Suspend all threads of a Windows process."""
    try:
        import ctypes
        import ctypes.wintypes
        THREAD_SUSPEND_RESUME = 0x0002
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)  # type: ignore[attr-defined]
        snapshot = kernel32.CreateToolhelp32Snapshot(0x00000004, pid)
        if snapshot == -1:
            return
        class THREADENTRY32(ctypes.Structure):
            _fields_ = [
                ("dwSize", ctypes.wintypes.DWORD),
                ("cntUsage", ctypes.wintypes.DWORD),
                ("th32ThreadID", ctypes.wintypes.DWORD),
                ("th32OwnerProcessID", ctypes.wintypes.DWORD),
                ("tpBasePri", ctypes.c_long),
                ("tpDeltaPri", ctypes.c_long),
                ("dwFlags", ctypes.wintypes.DWORD),
            ]
        te = THREADENTRY32()
        te.dwSize = ctypes.sizeof(THREADENTRY32)
        if kernel32.Thread32First(snapshot, ctypes.byref(te)):
            while True:
                if te.th32OwnerProcessID == pid:
                    thread_handle = kernel32.OpenThread(  # noqa: E501
                        THREAD_SUSPEND_RESUME, False, te.th32ThreadID
                    )
                    if thread_handle:
                        kernel32.SuspendThread(thread_handle)
                        kernel32.CloseHandle(thread_handle)
                if not kernel32.Thread32Next(snapshot, ctypes.byref(te)):
                    break
        kernel32.CloseHandle(snapshot)
    except Exception:
        pass


def _windows_resume(pid: int) -> None:
    """Resume all threads of a Windows process."""
    try:
        import ctypes
        import ctypes.wintypes
        THREAD_SUSPEND_RESUME = 0x0002
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)  # type: ignore[attr-defined]
        snapshot = kernel32.CreateToolhelp32Snapshot(0x00000004, pid)
        if snapshot == -1:
            return
        class THREADENTRY32(ctypes.Structure):
            _fields_ = [
                ("dwSize", ctypes.wintypes.DWORD),
                ("cntUsage", ctypes.wintypes.DWORD),
                ("th32ThreadID", ctypes.wintypes.DWORD),
                ("th32OwnerProcessID", ctypes.wintypes.DWORD),
                ("tpBasePri", ctypes.c_long),
                ("tpDeltaPri", ctypes.c_long),
                ("dwFlags", ctypes.wintypes.DWORD),
            ]
        te = THREADENTRY32()
        te.dwSize = ctypes.sizeof(THREADENTRY32)
        if kernel32.Thread32First(snapshot, ctypes.byref(te)):
            while True:
                if te.th32OwnerProcessID == pid:
                    thread_handle = kernel32.OpenThread(  # noqa: E501
                        THREAD_SUSPEND_RESUME, False, te.th32ThreadID
                    )
                    if thread_handle:
                        kernel32.ResumeThread(thread_handle)
                        kernel32.CloseHandle(thread_handle)
                if not kernel32.Thread32Next(snapshot, ctypes.byref(te)):
                    break
        kernel32.CloseHandle(snapshot)
    except Exception:
        pass
