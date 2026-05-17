"""Hashcat verification."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class HashcatVerificationResult:
    executable_path: Path
    ok: bool
    exit_code: int | None
    stdout: str
    stderr: str
    version_text: str | None
    error: str | None = None


def verify_hashcat(executable_path: Path, timeout_seconds: int = 10) -> HashcatVerificationResult:
    """Run hashcat --version as an argument array."""
    executable_path = executable_path.resolve()
    if not executable_path.exists() or not executable_path.is_file():
        return HashcatVerificationResult(
            executable_path=executable_path,
            ok=False,
            exit_code=None,
            stdout="",
            stderr="",
            version_text=None,
            error="Hashcat executable does not exist or is not a file.",
        )

    args = [str(executable_path), "--version"]
    try:
        completed = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except OSError as exc:
        return HashcatVerificationResult(
            executable_path=executable_path,
            ok=False,
            exit_code=None,
            stdout="",
            stderr="",
            version_text=None,
            error=str(exc),
        )
    except subprocess.TimeoutExpired:
        return HashcatVerificationResult(
            executable_path=executable_path,
            ok=False,
            exit_code=None,
            stdout="",
            stderr="",
            version_text=None,
            error="Hashcat version check timed out.",
        )

    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    version_text = stdout.splitlines()[0] if stdout else None
    return HashcatVerificationResult(
        executable_path=executable_path,
        ok=completed.returncode == 0 and bool(version_text),
        exit_code=completed.returncode,
        stdout=stdout,
        stderr=stderr,
        version_text=version_text,
        error=None if completed.returncode == 0 else "Hashcat returned a non-zero exit code.",
    )
