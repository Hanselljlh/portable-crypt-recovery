"""PIM parsing and expansion."""

from __future__ import annotations

import re

_SPLIT_RE = re.compile(r"[,\n]+")
_RANGE_RE = re.compile(r"^(\d+)\s*-\s*(\d+)$")


def expand_pim_input(raw_input: str) -> list[int]:
    """Expand comma/newline separated PIM values and ranges."""
    values: list[int] = []
    for part in _SPLIT_RE.split(raw_input):
        token = part.strip()
        if not token:
            continue
        range_match = _RANGE_RE.match(token)
        if range_match:
            start = int(range_match.group(1))
            stop = int(range_match.group(2))
            if start <= 0 or stop <= 0:
                raise ValueError("PIM ranges must use positive integers.")
            if start > stop:
                raise ValueError(f"Invalid range: {token}")
            values.extend(range(start, stop + 1))
            continue
        if not token.isdigit():
            raise ValueError(f"Invalid PIM value: {token}")
        value = int(token)
        if value <= 0:
            raise ValueError("Use default PIM mode instead of entering 0.")
        values.append(value)
    if not values:
        raise ValueError("PIM list is empty.")
    return sorted(set(values))
