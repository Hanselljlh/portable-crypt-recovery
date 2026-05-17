"""Periodic autosave of workspace settings to workspace/settings.json."""

from __future__ import annotations

import contextlib
import threading

_timer: threading.Timer | None = None
_lock = threading.Lock()
_INTERVAL = 60


def start(interval: int = _INTERVAL) -> None:
    """Start the periodic autosave loop."""
    _schedule(interval)


def stop() -> None:
    """Cancel any pending autosave timer."""
    global _timer
    with _lock:
        if _timer is not None:
            _timer.cancel()
            _timer = None


def _schedule(interval: int) -> None:
    global _timer
    with _lock:
        _timer = threading.Timer(interval, _tick, args=(interval,))
        _timer.daemon = True
        _timer.start()


def _tick(interval: int) -> None:
    with contextlib.suppress(Exception):
        _save_settings()
    _schedule(interval)


def _save_settings() -> None:
    import json

    from portable_crypt_recovery.app.app_state import get_app_state
    from portable_crypt_recovery.core.atomic_write import atomic_write_json

    state = get_app_state()
    if not state.is_workspace_open():
        return

    settings_file = state.workspace_root / "settings.json"
    data: dict = {}
    if settings_file.exists():
        with contextlib.suppress(Exception):
            data = json.loads(settings_file.read_text(encoding="utf-8"))

    data["clipboard_auto_clear_seconds"] = state.clipboard_auto_clear_seconds
    data["default_queue_behavior_after_crack"] = state.queue_behavior_after_crack
    if state.hashcat_setup.executable_path:
        data["hashcat_path"] = str(state.hashcat_setup.executable_path)
        data["hashcat_verified"] = state.hashcat_setup.verified
        data["hashcat_version"] = state.hashcat_setup.version_string or ""
        data["selected_compute_devices"] = state.hashcat_setup.selected_compute_devices or []
    atomic_write_json(settings_file, data)
