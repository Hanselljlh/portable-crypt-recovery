"""In-memory workspace state holder."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from portable_crypt_recovery.models.hashcat_setup import HashcatSetup
from portable_crypt_recovery.models.queue_state import QueueState


@dataclass
class WorkspaceState:
    """In-memory state for the currently open workspace."""

    workspace_root: Path
    workspace_id: str = ""
    workspace_name: str = ""
    hashcat_setup: HashcatSetup = field(default_factory=HashcatSetup)
    queue_state: QueueState = field(default_factory=QueueState)
    target_count: int = 0
    header_count: int = 0
    is_dirty: bool = False  # unsaved changes

    def mark_dirty(self) -> None:
        self.is_dirty = True

    def mark_clean(self) -> None:
        self.is_dirty = False
