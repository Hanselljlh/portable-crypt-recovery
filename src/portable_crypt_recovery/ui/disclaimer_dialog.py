"""Startup disclaimer dialog — must be accepted before the app opens."""

from __future__ import annotations

_FALLBACK_TEXT = """\
PORTABLE VERACRYPT/TRUECRYPT RECOVERY GUI — DISCLAIMER

This software is provided for educational reference purposes only.  It was built
solely to solve one person's own personal volume-recovery problem.

USE ON ANY CONTAINER YOU DO NOT OWN IS UNAUTHORISED AND MAY CONSTITUTE
A CRIMINAL OFFENCE.

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

All data processed by this software is stored exclusively on your local device.
Nothing is transmitted to any server, cloud service, or remote destination.

See DISCLAIMER.md in the repository for the full terms.
Repository: https://github.com/Hanselljlh/portable-crypt-recovery
"""


class DisclaimerDialog:  # pragma: no cover
    """Modal disclaimer dialog shown at every launch.

    The user must scroll to the bottom of the text before the confirmation
    checkbox becomes enabled.  The Accept button is only enabled once the
    checkbox is ticked.  Declining (or closing) terminates the application.
    """

    def __new__(cls, parent=None):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QCheckBox,
            QDialog,
            QDialogButtonBox,
            QLabel,
            QPlainTextEdit,
            QPushButton,
            QVBoxLayout,
        )

        class _DisclaimerDialog(QDialog):
            def __init__(self, parent=None) -> None:
                super().__init__(parent)
                self.setWindowTitle("Legal Disclaimer and Terms of Use")
                self.setModal(True)
                self.resize(760, 600)
                # Prevent closing via the X button without declining explicitly
                self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, True)

                layout = QVBoxLayout(self)

                # Heading
                heading = QLabel(
                    "<b>Read the full disclaimer below before using this software.</b><br>"
                    "You must scroll to the bottom before you can accept."
                )
                heading.setWordWrap(True)
                layout.addWidget(heading)

                # Text area — read-only, tracks scroll position
                self._text = QPlainTextEdit()
                self._text.setReadOnly(True)
                self._text.setPlainText(self._load_disclaimer())
                layout.addWidget(self._text, 1)

                # Scroll-to-bottom notice
                self._scroll_notice = QLabel(
                    "↓  Scroll to the bottom to enable the checkbox."
                )
                self._scroll_notice.setStyleSheet("color: #888;")
                layout.addWidget(self._scroll_notice)

                # Checkbox
                self._chk = QCheckBox(
                    "I have read the entire disclaimer and accept all terms."
                )
                self._chk.setEnabled(False)
                self._chk.toggled.connect(self._on_chk_toggled)
                layout.addWidget(self._chk)

                # Buttons
                self._btn_box = QDialogButtonBox()
                self._btn_accept = QPushButton("Accept")
                self._btn_decline = QPushButton("Decline")
                self._btn_accept.setEnabled(False)
                self._btn_accept.setDefault(False)
                self._btn_decline.setDefault(True)
                self._btn_box.addButton(self._btn_accept, QDialogButtonBox.ButtonRole.AcceptRole)
                self._btn_box.addButton(self._btn_decline, QDialogButtonBox.ButtonRole.RejectRole)
                self._btn_box.accepted.connect(self.accept)
                self._btn_box.rejected.connect(self.reject)
                layout.addWidget(self._btn_box)

                # Connect scroll bar AFTER text is set
                sb = self._text.verticalScrollBar()
                sb.valueChanged.connect(self._on_scroll_changed)
                sb.rangeChanged.connect(self._on_range_changed)

                # Check immediately in case the text fits on screen without scrolling
                self._check_at_bottom()

            # ------------------------------------------------------------------
            def _load_disclaimer(self) -> str:
                from pathlib import Path

                from portable_crypt_recovery.core.paths import app_root_from_cwd

                candidate = app_root_from_cwd() / "DISCLAIMER.md"
                if candidate.exists():
                    try:
                        return candidate.read_text(encoding="utf-8")
                    except OSError:
                        pass

                # Try next to package root (two levels up from this file)
                pkg_root = Path(__file__).resolve().parent.parent.parent.parent
                candidate2 = pkg_root / "DISCLAIMER.md"
                if candidate2.exists():
                    try:
                        return candidate2.read_text(encoding="utf-8")
                    except OSError:
                        pass

                return _FALLBACK_TEXT

            def _check_at_bottom(self) -> None:
                sb = self._text.verticalScrollBar()
                at_bottom = sb.value() >= sb.maximum() - 4
                if at_bottom:
                    self._chk.setEnabled(True)
                    self._scroll_notice.setVisible(False)

            def _on_scroll_changed(self, _value: int) -> None:
                self._check_at_bottom()

            def _on_range_changed(self, _min: int, _max: int) -> None:
                # If the range is zero, the text fits without scrolling — enable checkbox
                self._check_at_bottom()

            def _on_chk_toggled(self, checked: bool) -> None:
                self._btn_accept.setEnabled(checked)
                if checked:
                    self._btn_accept.setDefault(True)
                    self._btn_decline.setDefault(False)
                else:
                    self._btn_accept.setDefault(False)
                    self._btn_decline.setDefault(True)

        return _DisclaimerDialog(parent)
