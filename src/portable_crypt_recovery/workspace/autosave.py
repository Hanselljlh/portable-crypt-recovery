"""60-second autosave loop for queue-state.json."""

from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import Path


class AutosaveLoop:
    """Periodically saves queue state using atomic writes.

    The callback is called every ``interval_seconds`` seconds while running.
    It should be a zero-argument callable that performs the save.
    """

    def __init__(
        self,
        save_callback: Callable[[], None],
        interval_seconds: float = 60.0,
    ) -> None:
        self._save_callback = save_callback
        self._interval = interval_seconds
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()
        self._running = False

    def start(self) -> None:
        """Start the autosave loop."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._schedule_next()

    def stop(self) -> None:
        """Stop the autosave loop."""
        with self._lock:
            self._running = False
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None

    def save_now(self) -> None:
        """Trigger an immediate save outside of the timer."""
        self._save_callback()

    def _schedule_next(self) -> None:
        if not self._running:
            return
        self._timer = threading.Timer(self._interval, self._tick)
        self._timer.daemon = True
        self._timer.start()

    def _tick(self) -> None:
        try:
            self._save_callback()
        finally:
            with self._lock:
                if self._running:
                    self._schedule_next()


def make_queue_state_saver(
    workspace_root: Path,
    get_queue_state_dict: Callable[[], dict],
) -> Callable[[], None]:
    """Return a callback that atomically writes queue-state.json."""
    from portable_crypt_recovery.core.atomic_write import atomic_write_json

    queue_state_path = workspace_root / "queue" / "queue-state.json"

    def save() -> None:
        data = get_queue_state_dict()
        atomic_write_json(queue_state_path, data)

    return save
