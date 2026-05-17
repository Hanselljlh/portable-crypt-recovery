"""Log sanitizer — strips lines containing passwords or cracked result patterns."""

from __future__ import annotations

import re
from pathlib import Path

# Patterns that suggest a line contains sensitive data
_SENSITIVE_PATTERNS = [
    re.compile(r"(?i)password\s*[:=]"),
    re.compile(r"(?i)cracked\s*[:=]"),
    re.compile(r"(?i)recovered\s*[:=]"),
    re.compile(r"\$veracrypt\$"),
    re.compile(r"\$truecrypt\$"),
]


def sanitize_log_file(log_path: Path) -> list[str]:
    """Read a log file and return lines with sensitive content removed.

    Parameters
    ----------
    log_path:
        Path to the log file.

    Returns
    -------
    list[str]
        Clean lines (sensitive lines replaced with a placeholder).
    """
    if not log_path.exists():
        return []
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    return [_sanitize_line(line) for line in lines]


def _sanitize_line(line: str) -> str:
    for pattern in _SENSITIVE_PATTERNS:
        if pattern.search(line):
            return "[LINE REDACTED — may contain sensitive data]"
    return line


def sanitize_log_text(text: str) -> str:
    """Sanitize a string of log text."""
    return "\n".join(_sanitize_line(line) for line in text.splitlines())
