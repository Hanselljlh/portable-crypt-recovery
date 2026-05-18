"""Tests for clipboard auto-clear — verifies main-thread safety via QTimer."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch


def _make_pyside6_mocks(cb_text: str = ""):
    """Return (sys.modules patch dict, mock_cb, mock_timer_cls, mock_timer)."""
    mock_cb = MagicMock()
    mock_cb.text.return_value = cb_text

    mock_app_cls = MagicMock()
    mock_app_cls.clipboard.return_value = mock_cb

    mock_timer = MagicMock()
    mock_timer_cls = MagicMock(return_value=mock_timer)

    mock_qtwidgets = MagicMock()
    mock_qtwidgets.QApplication = mock_app_cls

    mock_qtcore = MagicMock()
    mock_qtcore.QTimer = mock_timer_cls

    patches = {
        "PySide6": MagicMock(),
        "PySide6.QtWidgets": mock_qtwidgets,
        "PySide6.QtCore": mock_qtcore,
    }
    return patches, mock_cb, mock_timer_cls, mock_timer


def _reset_state():
    import portable_crypt_recovery.core.clipboard as m
    m._qt_timer = None
    m._pending_text = ""


# ---------------------------------------------------------------------------
# Safety: no threading.Timer usage
# ---------------------------------------------------------------------------


def test_clipboard_does_not_use_threading_timer():
    """clipboard.py must not use threading.Timer — it is not Qt-main-thread-safe."""
    import inspect

    import portable_crypt_recovery.core.clipboard as m

    src = inspect.getsource(m)
    assert "threading.Timer" not in src
    assert "import threading" not in src


# ---------------------------------------------------------------------------
# copy_with_auto_clear — normal path
# ---------------------------------------------------------------------------


def test_copy_with_auto_clear_sets_clipboard_text():
    """copy_with_auto_clear must call clipboard().setText with the given text."""
    _reset_state()
    patches, mock_cb, _, _ = _make_pyside6_mocks()
    with patch.dict(sys.modules, patches):
        import portable_crypt_recovery.core.clipboard as m
        m.copy_with_auto_clear("my-secret", clear_after_seconds=60)
    mock_cb.setText.assert_called_once_with("my-secret")


def test_copy_with_auto_clear_creates_single_shot_qtimer():
    """copy_with_auto_clear must use QTimer.setSingleShot(True), not threading.Timer."""
    _reset_state()
    patches, _, mock_timer_cls, mock_timer = _make_pyside6_mocks()
    with patch.dict(sys.modules, patches):
        import portable_crypt_recovery.core.clipboard as m
        m.copy_with_auto_clear("secret", clear_after_seconds=30)
    mock_timer_cls.assert_called_once()
    mock_timer.setSingleShot.assert_called_with(True)
    mock_timer.start.assert_called_with(30_000)


def test_copy_with_auto_clear_reuses_timer_on_second_call():
    """Calling copy_with_auto_clear again must restart the existing QTimer, not create a new one."""
    _reset_state()
    patches, _, mock_timer_cls, mock_timer = _make_pyside6_mocks()
    with patch.dict(sys.modules, patches):
        import portable_crypt_recovery.core.clipboard as m
        m.copy_with_auto_clear("first", clear_after_seconds=60)
        m.copy_with_auto_clear("second", clear_after_seconds=60)
    # QTimer() constructed only once
    assert mock_timer_cls.call_count == 1
    # start() called twice (once per copy_with_auto_clear call)
    assert mock_timer.start.call_count == 2


# ---------------------------------------------------------------------------
# copy_with_auto_clear — zero / negative seconds skips timer
# ---------------------------------------------------------------------------


def test_copy_with_auto_clear_zero_seconds_skips_timer():
    """With clear_after_seconds=0, no QTimer must be created."""
    _reset_state()
    patches, _, mock_timer_cls, mock_timer = _make_pyside6_mocks()
    with patch.dict(sys.modules, patches):
        import portable_crypt_recovery.core.clipboard as m
        m.copy_with_auto_clear("text", clear_after_seconds=0)
    mock_timer_cls.assert_not_called()
    mock_timer.start.assert_not_called()


# ---------------------------------------------------------------------------
# _do_clear — conditional clear logic
# ---------------------------------------------------------------------------


def test_do_clear_clears_when_text_matches():
    """_do_clear must clear the clipboard when it still holds our text."""
    _reset_state()
    patches, mock_cb, _, _ = _make_pyside6_mocks(cb_text="secret")
    with patch.dict(sys.modules, patches):
        import portable_crypt_recovery.core.clipboard as m
        m._pending_text = "secret"
        m._do_clear()
    mock_cb.clear.assert_called_once()


def test_do_clear_does_not_clear_when_text_changed():
    """_do_clear must NOT clear if the clipboard was overwritten by something else."""
    _reset_state()
    patches, mock_cb, _, _ = _make_pyside6_mocks(cb_text="user_changed_this")
    with patch.dict(sys.modules, patches):
        import portable_crypt_recovery.core.clipboard as m
        m._pending_text = "secret"
        m._do_clear()
    mock_cb.clear.assert_not_called()
