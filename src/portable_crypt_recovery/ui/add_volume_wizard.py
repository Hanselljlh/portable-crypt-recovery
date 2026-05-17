"""Add Volume wizard dialog."""

from __future__ import annotations


class AddVolumeWizard:  # pragma: no cover
    """Wizard for adding a new target volume."""

    def __new__(cls, parent=None):
        from PySide6.QtWidgets import (
            QCheckBox,
            QComboBox,
            QDialog,
            QDialogButtonBox,
            QFileDialog,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QPushButton,
            QVBoxLayout,
        )

        class _AddVolumeWizard(QDialog):
            def __init__(self, parent=None) -> None:
                super().__init__(parent)
                self.setWindowTitle("Add Volume")
                self.resize(600, 400)
                layout = QVBoxLayout(self)

                # Ownership confirmation
                ownership_group = QGroupBox("Ownership Confirmation")
                ownership_layout = QVBoxLayout(ownership_group)
                self.chk_ownership = QCheckBox(
                    "I confirm I own or am authorized to recover this volume."
                )
                ownership_layout.addWidget(self.chk_ownership)
                layout.addWidget(ownership_group)

                # Source type
                type_group = QGroupBox("Source Type")
                type_layout = QVBoxLayout(type_group)
                self.cmb_source_type = QComboBox()
                self.cmb_source_type.addItems([
                    "File Container",
                    "Disk/Drive Image",
                    "Already Extracted Header",
                ])
                type_layout.addWidget(self.cmb_source_type)
                # Future options (disabled)
                lbl_future = QLabel(
                    "Raw Physical Disk — Future | Raw Physical Partition — Future"
                )
                lbl_future.setStyleSheet("color: gray; font-style: italic;")
                type_layout.addWidget(lbl_future)
                layout.addWidget(type_group)

                # File browse
                browse_group = QGroupBox("Source File")
                browse_layout = QHBoxLayout(browse_group)
                self.txt_path = QLineEdit()
                self.txt_path.setPlaceholderText("Browse for source file...")
                btn_browse = QPushButton("Browse...")
                btn_browse.clicked.connect(self._browse_file)
                browse_layout.addWidget(self.txt_path)
                browse_layout.addWidget(btn_browse)
                layout.addWidget(browse_group)

                # Header extraction options
                extract_group = QGroupBox("Header Candidates to Extract")
                extract_layout = QVBoxLayout(extract_group)
                self.chk_normal = QCheckBox("Normal/Outer Volume Header (offset 0)")
                self.chk_hidden = QCheckBox("Hidden Volume Header (offset 65536)")
                self.chk_system = QCheckBox("System Header (offset 31744)")
                self.chk_normal.setChecked(True)
                self.chk_hidden.setChecked(True)
                extract_layout.addWidget(self.chk_normal)
                extract_layout.addWidget(self.chk_hidden)
                extract_layout.addWidget(self.chk_system)
                layout.addWidget(extract_group)

                # Buttons
                buttons = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                )
                buttons.accepted.connect(self._on_accept)
                buttons.rejected.connect(self.reject)
                layout.addWidget(buttons)

            def _browse_file(self) -> None:
                path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Select Volume or Header File",
                    "",
                    "All Files (*.*)",
                )
                if path:
                    self.txt_path.setText(path)

            def _on_accept(self) -> None:
                from PySide6.QtWidgets import QMessageBox
                if not self.chk_ownership.isChecked():
                    QMessageBox.warning(
                        self,
                        "Ownership Required",
                        "You must confirm ownership before adding a volume.",
                    )
                    return
                if not self.txt_path.text().strip():
                    QMessageBox.warning(self, "No File", "Please select a source file.")
                    return
                self.accept()

        return _AddVolumeWizard(parent)
