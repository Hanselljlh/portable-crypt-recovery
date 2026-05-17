"""Parse supported Hashcat modes from hashcat --help output."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

# Pattern: "  13711 | VeraCrypt PBKDF2-HMAC-RIPEMD160 + XTS 512-bit            | Full-Disk Encryption (FDE)"
_MODE_LINE_RE = re.compile(r"^\s*(\d+)\s*\|\s*(.+?)\s*\|")


def scan_supported_modes(
    hashcat_executable: Path,
    timeout_seconds: int = 30,
) -> dict[int, str]:
    """Run hashcat --help and parse the supported mode list.

    Returns
    -------
    dict[int, str]
        Mapping of mode_number -> label for all modes reported by the binary.
        Returns empty dict on failure.
    """
    args = [str(hashcat_executable.resolve()), "--help"]
    try:
        result = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}

    return _parse_help_output(result.stdout + result.stderr)


def _parse_help_output(output: str) -> dict[int, str]:
    """Extract mode numbers and labels from hashcat --help text."""
    modes: dict[int, str] = {}
    in_hash_modes = False
    for line in output.splitlines():
        # Section headers
        if "Hash-Mode" in line and "Hash-Name" in line:
            in_hash_modes = True
            continue
        if in_hash_modes:
            # End of section (blank line after content)
            m = _MODE_LINE_RE.match(line)
            if m:
                mode_num = int(m.group(1))
                label = m.group(2).strip()
                modes[mode_num] = label
    return modes
