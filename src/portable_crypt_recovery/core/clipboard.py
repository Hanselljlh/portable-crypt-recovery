"""Clipboard helpers — copy with timed auto-clear."""

from __future__ import annotations

import threading

DEFAULT_CLIPBOARD_CLEAR_SECONDS = 60

_clear_timer: threading.Timer | None = None
_timer_lock = threading.Lock()


def copy_with_auto_clear(text: str, clear_after_seconds: int = DEFAULT_CLIPBOARD_CLEAR_SECONDS) -> None:
    """Copy text to the system clipboard and clear it after ``clear_after_seconds``.

    Requires a running Qt application (uses QApplication.clipboard()).
    If ``clear_after_seconds`` is 0 or negative the clipboard is not auto-cleared.
    """
    global _clear_timer

    from PySide6.QtWidgets import QApplication
    cb = QApplication.clipboard()
    cb.setText(text)

    if clear_after_seconds <= 0:
        return

    with _timer_lock:
        if _clear_timer is not None:
            _clear_timer.cancel()
        _clear_timer = threading.Timer(clear_after_seconds, _do_clear, args=(text,))
        _clear_timer.daemon = True
        _clear_timer.start()


def _do_clear(original_text: str) -> None:
    """Clear clipboard only if it still contains the text we put there."""
    global _clear_timer
    try:
        from PySide6.QtWidgets import QApplication
        cb = QApplication.clipboard()
        if cb.text() == original_text:
            cb.clear()
    except Exception:
        pass
    with _timer_lock:
        _clear_timer = None
