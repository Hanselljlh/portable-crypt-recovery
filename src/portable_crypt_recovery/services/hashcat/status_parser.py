"""Parse Hashcat --status-json output lines."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass
class HashcatStatus:
    """Parsed snapshot of a Hashcat status report."""

    progress_cur: int = 0
    progress_total: int = 0
    progress_percent: float = 0.0
    speed_hashes_per_sec: int = 0
    estimated_finish: str | None = None
    status: str = ""  # e.g. "Running", "Exhausted", "Cracked"
    raw: dict[str, Any] | None = None


def parse_status_line(line: str) -> HashcatStatus | None:
    """Try to parse a Hashcat JSON status line.

    Returns None if the line is not a valid JSON status object.
    """
    line = line.strip()
    if not line.startswith("{"):
        return None
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None

    if "status" not in data and "progress" not in data:
        return None

    progress = data.get("progress", [0, 0])
    cur = int(progress[0]) if len(progress) > 0 else 0
    total = int(progress[1]) if len(progress) > 1 else 0
    pct = (cur / total * 100.0) if total > 0 else 0.0

    # Speed: list of integers (one per device)
    speed_list = data.get("speed", [])
    speed = sum(int(s) for s in speed_list) if speed_list else 0

    estimated = data.get("estimated_stop")
    if isinstance(estimated, str):
        pass  # already a string
    elif isinstance(estimated, (int, float)):
        estimated = str(estimated)
    else:
        estimated = None

    status_str = str(data.get("status", ""))

    return HashcatStatus(
        progress_cur=cur,
        progress_total=total,
        progress_percent=round(pct, 2),
        speed_hashes_per_sec=speed,
        estimated_finish=estimated,
        status=status_str,
        raw=data,
    )


def parse_status_lines(lines: list[str]) -> list[HashcatStatus]:
    """Parse a list of output lines and return all valid status snapshots."""
    results = []
    for line in lines:
        parsed = parse_status_line(line)
        if parsed is not None:
            results.append(parsed)
    return results
