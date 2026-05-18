"""Clipboard helpers — copy with timed auto-clear."""

from __future__ import annotations

DEFAULT_CLIPBOARD_CLEAR_SECONDS = 60

_pending_text: str = ""
_qt_timer = None  # QTimer instance, created lazily on first use


def copy_with_auto_clear(
    text: str, clear_after_seconds: int = DEFAULT_CLIPBOARD_CLEAR_SECONDS
) -> None:
    """Copy text to the system clipboard and clear it after ``clear_after_seconds``.

    Requires a running Qt application (uses QApplication.clipboard()).
    If ``clear_after_seconds`` is 0 or negative the clipboard is not auto-cleared.

    The auto-clear timer runs on the Qt main thread via QTimer so it is safe
    to call clipboard APIs from the timeout slot.
    """
    global _pending_text, _qt_timer

    from PySide6.QtWidgets import QApplication
    cb = QApplication.clipboard()
    cb.setText(text)

    if clear_after_seconds <= 0:
        return

    _pending_text = text

    from PySide6.QtCore import QTimer
    if _qt_timer is None:
        _qt_timer = QTimer()
        _qt_timer.setSingleShot(True)
        _qt_timer.timeout.connect(_do_clear)

    # Calling start() on an already-running single-shot QTimer restarts it,
    # cancelling the previous countdown — equivalent to cancel+restart.
    _qt_timer.start(clear_after_seconds * 1000)


def _do_clear() -> None:
    """Clear clipboard only if it still contains the text we put there.

    Called from the QTimer timeout signal — always runs on the Qt main thread.
    """
    global _pending_text
    try:
        from PySide6.QtWidgets import QApplication
        cb = QApplication.clipboard()
        if cb.text() == _pending_text:
            cb.clear()
    except Exception:
        pass
    _pending_text = ""
