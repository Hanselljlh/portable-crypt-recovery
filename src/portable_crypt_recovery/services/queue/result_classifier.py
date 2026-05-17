"""Classify Hashcat job results after completion.

Reads potfile/outfile BEFORE generating full reports to ensure crack is never lost.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ClassificationResult:
    status: str  # "cracked" | "exhausted" | "failed"
    cracked_password: str | None = None
    raw_outfile_line: str | None = None
    exit_code: int | None = None


def classify_result(
    exit_code: int | None,
    outfile_path: Path,
    potfile_path: Path,
) -> ClassificationResult:
    """Determine job outcome by reading outfile and potfile.

    This function is called BEFORE any report generation to ensure
    the cracked password is recorded first.

    Parameters
    ----------
    exit_code:
        Hashcat process exit code.
    outfile_path:
        Absolute path to the Hashcat --outfile.
    potfile_path:
        Absolute path to the Hashcat --potfile-path.
    """
    # Check outfile first (preferred — contains structured cracked output)
    cracked_line = _read_cracked_from_file(outfile_path)
    if cracked_line is None:
        cracked_line = _read_cracked_from_potfile(potfile_path)

    if cracked_line is not None:
        password = _extract_password(cracked_line)
        return ClassificationResult(
            status="cracked",
            cracked_password=password,
            raw_outfile_line=cracked_line,
            exit_code=exit_code,
        )

    # Exit code 0 = exhausted, non-zero = failed
    if exit_code == 0:
        return ClassificationResult(status="exhausted", exit_code=exit_code)
    return ClassificationResult(status="failed", exit_code=exit_code)


def _read_cracked_from_file(path: Path) -> str | None:
    """Return the first non-empty line from outfile, or None."""
    if not path.exists():
        return None
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line:
                return line
    except OSError:
        pass
    return None


def _read_cracked_from_potfile(path: Path) -> str | None:
    """Return the last cracked line from potfile, or None."""
    if not path.exists():
        return None
    try:
        lines = [
            line.strip()
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip()
        ]
        return lines[-1] if lines else None
    except OSError:
        return None


def _extract_password(line: str) -> str:
    """Extract password from a hash:password line.

    Hashcat outfile format: <hash>:<password>
    We return everything after the last colon.
    """
    if ":" in line:
        return line.split(":", 1)[-1]
    return line
