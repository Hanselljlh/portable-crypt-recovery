"""Targets view — list and manage recovery targets."""

from __future__ import annotations


class TargetsView:  # pragma: no cover
    """List of targets with Add/View/Remove actions.

    'Add Volume' wizard: ownership confirmation, source type, browse, extract headers.
    Raw physical device options shown as disabled 'Future' labels.
    """

    def __new__(cls):
        from PySide6.QtWidgets import (
            QHBoxLayout,
            QLabel,
            QListWidget,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

        class _TargetsView(QWidget):
            def __init__(self) -> None:
                super().__init__()
                layout = QVBoxLayout(self)

                # Toolbar
                toolbar = QHBoxLayout()
                self.btn_add = QPushButton("Add Volume...")
                self.btn_view_headers = QPushButton("View Headers")
                self.btn_remove = QPushButton("Remove Target")
                toolbar.addWidget(self.btn_add)
                toolbar.addWidget(self.btn_view_headers)
                toolbar.addWidget(self.btn_remove)
                toolbar.addStretch()
                layout.addLayout(toolbar)

                # Target list
                self.target_list = QListWidget()
                layout.addWidget(self.target_list, 1)

                # Future placeholder
                future_lbl = QLabel(
                    "Raw physical disk/drive/partition access: Future (not available in v1)"
                )
                future_lbl.setStyleSheet("color: gray; font-style: italic;")
                layout.addWidget(future_lbl)

                # Wire signals
                self.btn_add.clicked.connect(self._open_add_wizard)
                self.btn_view_headers.clicked.connect(self._view_headers)
                self.btn_remove.clicked.connect(self._remove_target)

            def _open_add_wizard(self) -> None:
                from portable_crypt_recovery.ui.add_volume_wizard import AddVolumeWizard
                wizard = AddVolumeWizard(parent=self)
                wizard.exec()

            def _view_headers(self) -> None:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "View Headers", "Select a target to view its headers.")

            def _remove_target(self) -> None:
                from PySide6.QtWidgets import QMessageBox
                item = self.target_list.currentItem()
                if item is None:
                    QMessageBox.warning(self, "Remove Target", "No target selected.")

        return _TargetsView()
