"""Password candidate builder foundation."""

from __future__ import annotations

from itertools import product


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)
    return output


def combine_segments(segments: list[list[str]]) -> list[str]:
    """Combine ordered segment variants and preserve first-seen order."""
    if not segments:
        return []
    return dedupe_preserve_order(["".join(parts) for parts in product(*segments)])
