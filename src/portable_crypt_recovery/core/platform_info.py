"""Platform information."""

from __future__ import annotations

import platform


def platform_summary() -> dict[str, str]:
    """Return basic platform details for workspace metadata and diagnostics."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }
