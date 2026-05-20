"""Tests for the disclaimer dialog and application startup accept/reject flow."""

from __future__ import annotations

import sys

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_app():
    """Return (or reuse) a QApplication instance."""
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication(sys.argv)


# ---------------------------------------------------------------------------
# QDialog accept code
# ---------------------------------------------------------------------------

def test_qdialog_accepted_code_is_1():
    """QDialog.DialogCode.Accepted must equal 1 — this is what exec() returns."""
    _make_app()
    from PySide6.QtWidgets import QDialog
    assert int(QDialog.DialogCode.Accepted) == 1


def test_qdialog_rejected_code_is_0():
    _make_app()
    from PySide6.QtWidgets import QDialog
    assert int(QDialog.DialogCode.Rejected) == 0


def test_accepted_comparison_matches_int_1():
    """exec() returns an int; confirm it compares equal to DialogCode.Accepted."""
    _make_app()
    from PySide6.QtWidgets import QDialog
    assert QDialog.DialogCode.Accepted == 1
    assert QDialog.DialogCode.Accepted != 0


# ---------------------------------------------------------------------------
# DisclaimerDialog instantiation and initial state
# ---------------------------------------------------------------------------

def test_disclaimer_dialog_is_qdialog_subclass():
    _make_app()
    from PySide6.QtWidgets import QDialog

    from portable_crypt_recovery.ui.disclaimer_dialog import DisclaimerDialog
    dlg = DisclaimerDialog()
    assert isinstance(dlg, QDialog)


def test_disclaimer_dialog_accept_button_initially_disabled():
    """Accept button must be disabled until the user scrolls and checks the box."""
    _make_app()
    from portable_crypt_recovery.ui.disclaimer_dialog import DisclaimerDialog
    dlg = DisclaimerDialog()
    assert not dlg._btn_accept.isEnabled()


def test_disclaimer_dialog_checkbox_initially_disabled():
    """Checkbox must be disabled until scroll-to-bottom is reached."""
    _make_app()
    from portable_crypt_recovery.ui.disclaimer_dialog import DisclaimerDialog
    dlg = DisclaimerDialog()
    assert not dlg._chk.isEnabled()


def test_disclaimer_dialog_decline_button_always_enabled():
    _make_app()
    from portable_crypt_recovery.ui.disclaimer_dialog import DisclaimerDialog
    dlg = DisclaimerDialog()
    assert dlg._btn_decline.isEnabled()


# ---------------------------------------------------------------------------
# Accept flow — checkbox enables accept button
# ---------------------------------------------------------------------------

def test_disclaimer_accept_flow():
    """Enabling the checkbox must enable the Accept button."""
    _make_app()
    from portable_crypt_recovery.ui.disclaimer_dialog import DisclaimerDialog
    dlg = DisclaimerDialog()

    # Simulate scroll reaching bottom
    dlg._chk.setEnabled(True)
    dlg._scroll_notice.setVisible(False)

    # Tick the checkbox
    dlg._chk.setChecked(True)
    assert dlg._btn_accept.isEnabled()

    # Untick — accept must be disabled again
    dlg._chk.setChecked(False)
    assert not dlg._btn_accept.isEnabled()


def test_disclaimer_accept_dialog_returns_accepted_code():
    """Calling accept() must make the dialog result equal QDialog.DialogCode.Accepted."""
    _make_app()
    from PySide6.QtWidgets import QDialog

    from portable_crypt_recovery.ui.disclaimer_dialog import DisclaimerDialog
    dlg = DisclaimerDialog()
    dlg.accept()
    assert dlg.result() == QDialog.DialogCode.Accepted


def test_disclaimer_reject_dialog_returns_rejected_code():
    _make_app()
    from PySide6.QtWidgets import QDialog

    from portable_crypt_recovery.ui.disclaimer_dialog import DisclaimerDialog
    dlg = DisclaimerDialog()
    dlg.reject()
    assert dlg.result() == QDialog.DialogCode.Rejected


# ---------------------------------------------------------------------------
# application.py comparison guard
# ---------------------------------------------------------------------------

def test_application_comparison_does_not_raise():
    """The exact comparison used in application.py must not raise AttributeError."""
    _make_app()
    from PySide6.QtWidgets import QDialog

    from portable_crypt_recovery.ui.disclaimer_dialog import DisclaimerDialog
    dlg = DisclaimerDialog()
    dlg.accept()

    # This is the exact expression from application.py — must not AttributeError
    comparison_ok = dlg.result() != QDialog.DialogCode.Accepted
    assert comparison_ok is False  # accepted → result() == Accepted → comparison is False


def test_application_reject_stops_app():
    """Rejecting must make result() != Accepted (so run_app would return 0)."""
    _make_app()
    from PySide6.QtWidgets import QDialog

    from portable_crypt_recovery.ui.disclaimer_dialog import DisclaimerDialog
    dlg = DisclaimerDialog()
    dlg.reject()
    assert dlg.result() != QDialog.DialogCode.Accepted
