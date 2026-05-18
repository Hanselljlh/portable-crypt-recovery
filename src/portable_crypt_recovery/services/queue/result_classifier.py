"""Classify Hashcat job results after completion.

Reads potfile/outfile BEFORE generating full reports to ensure crack is never lost.

Hashcat exit codes (from src/hashcat.c RC_FINAL_* constants):
  0 = CRACKED       – at least one hash was found
  1 = EXHAUSTED     – all candidates tried, no match
  2 = ABORTED       – user quit (q / Ctrl-C) or stop_and_discard
  3 = ABORTED_CHECKPOINT
  4 = ABORTED_RUNTIME
  5 = ABORTED_FINISH
 -1 = ERROR         – returned as 4294967295 (0xFFFFFFFF) on Windows
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ClassificationResult:
    status: str  # "cracked" | "exhausted" | "aborted" | "failed"
    cracked_password: str | None = None
    raw_outfile_line: str | None = None
    exit_code: int | None = None


def classify_result(
    exit_code: int | None,
    outfile_path: Path,
    potfile_path: Path,
) -> ClassificationResult:
    """Determine job outcome by reading outfile/potfile then checking exit code.

    Outfile/potfile are checked first so a cracked password is never lost even
    if the exit code is unexpected.
    """
    # Always check outfile / potfile first — a cracked result is the highest
    # priority regardless of exit code.
    cracked_line = _read_cracked_from_file(outfile_path)
    if cracked_line is None:
        cracked_line = _read_cracked_from_potfile(potfile_path)

    if cracked_line is not None:
        return ClassificationResult(
            status="cracked",
            cracked_password=_extract_password(cracked_line),
            raw_outfile_line=cracked_line,
            exit_code=exit_code,
        )

    # Map exit code to status.
    # Note: exit code 0 here means hashcat reported CRACKED but no output
    # file content was found — treat conservatively as cracked (empty outfile).
    if exit_code == 0:
        # CRACKED exit but outfile was empty; shouldn't normally happen.
        # Record as cracked with no password so the user can investigate.
        return ClassificationResult(status="cracked", exit_code=exit_code)

    if exit_code == 1:
        # EXHAUSTED — all candidates tried, hash not cracked.
        return ClassificationResult(status="exhausted", exit_code=exit_code)

    if exit_code in (2, 3, 4, 5):
        # ABORTED — user or runtime stopped the run; job can be re-queued.
        return ClassificationResult(status="aborted", exit_code=exit_code)

    # -1 / 4294967295 / anything else → error
    return ClassificationResult(status="failed", exit_code=exit_code)


def _read_cracked_from_file(path: Path) -> str | None:
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
    if not path.exists():
        return None
    try:
        lines = [
            ln.strip()
            for ln in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if ln.strip()
        ]
        return lines[-1] if lines else None
    except OSError:
        return None


def _extract_password(line: str) -> str:
    """Extract password from a hash:password line (everything after first colon)."""
    if ":" in line:
        return line.split(":", 1)[-1]
    return line
