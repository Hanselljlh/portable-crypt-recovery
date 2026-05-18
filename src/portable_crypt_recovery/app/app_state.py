"""Central application state."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from portable_crypt_recovery.models.hashcat_setup import HashcatSetup
from portable_crypt_recovery.models.queue_state import QueueState


@dataclass
class AppState:
    """Singleton-style holder for all mutable application state.

    One instance lives for the lifetime of the application session.
    Views read from and write to this object rather than to JSON files directly.
    """

    # Active workspace
    workspace_root: Path | None = None
    workspace_id: str = ""
    workspace_name: str = ""

    # Hashcat configuration
    hashcat_setup: HashcatSetup = field(default_factory=HashcatSetup)

    # Queue state (in memory; autosaved periodically)
    queue_state: QueueState = field(default_factory=QueueState)

    # Counts (refreshed when workspace changes)
    target_count: int = 0
    header_count: int = 0
    job_count: int = 0

    # Preferences (loaded from workspace settings.json)
    clipboard_auto_clear_seconds: int = 60
    queue_behavior_after_crack: str = "continue_other_uncracked_targets"

    # Dirty flag: unsaved queue state
    _queue_dirty: bool = False

    def is_workspace_open(self) -> bool:
        return self.workspace_root is not None

    def is_hashcat_ready(self) -> bool:
        return self.hashcat_setup.verified and self.hashcat_setup.executable_path is not None

    def mark_queue_dirty(self) -> None:
        self._queue_dirty = True

    def mark_queue_clean(self) -> None:
        self._queue_dirty = False

    def load_from_workspace(self, workspace_root: Path, record: dict[str, Any]) -> None:
        """Populate state from an opened workspace record."""
        self.workspace_root = workspace_root
        self.workspace_id = record.get("workspace_id", "")
        self.workspace_name = record.get("workspace_name", workspace_root.name)

    def load_settings(self, settings: dict[str, Any]) -> None:
        """Populate preferences from workspace settings.json."""
        self.clipboard_auto_clear_seconds = int(
            settings.get("clipboard_auto_clear_seconds", 60)
        )
        self.queue_behavior_after_crack = settings.get(
            "default_queue_behavior_after_crack", "continue_other_uncracked_targets"
        )
        hc_path = settings.get("hashcat_path")
        if hc_path:
            self.hashcat_setup.executable_path = hc_path
            self.hashcat_setup.is_portable = not settings.get(
                "hashcat_path_is_external", False
            )
        # Load device IDs: try canonical key first, fall back to legacy key for
        # backward compatibility with workspaces saved before the rename.
        raw_ids = (
            settings.get("selected_device_ids")
            or settings.get("selected_compute_devices")
            or []
        )
        if raw_ids:
            self.hashcat_setup.selected_device_ids = [int(d) for d in raw_ids]
        if "use_optimized_kernels" in settings:
            self.hashcat_setup.use_optimized_kernels = bool(
                settings["use_optimized_kernels"]
            )
        if "use_cpu_opencl" in settings:
            self.hashcat_setup.use_cpu_opencl = bool(settings["use_cpu_opencl"])


# Module-level singleton
_app_state: AppState | None = None


def get_app_state() -> AppState:
    """Return the global AppState, creating it if needed."""
    global _app_state
    if _app_state is None:
        _app_state = AppState()
    return _app_state


def reset_app_state() -> None:
    """Reset the global AppState (used in tests)."""
    global _app_state
    _app_state = None
