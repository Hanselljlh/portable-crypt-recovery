"""Add Volume wizard dialog."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WizardResult:
    """Data collected by the Add Volume wizard after the user clicks OK."""
    source_path: str
    source_type: str          # "file_container" | "disk_image" | "extracted_header"
    container_family: str     # "veracrypt" | "truecrypt" | "unknown"
    extract_normal: bool
    extract_hidden: bool
    extract_system: bool


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
                self.resize(620, 460)
                self.result_data: WizardResult | None = None
                layout = QVBoxLayout(self)

                # Ownership confirmation
                ownership_group = QGroupBox("⚠ Ownership Confirmation")
                ownership_group.setStyleSheet(
                    "QGroupBox { border: 2px solid #cc3333; border-radius: 4px; "
                    "margin-top: 6px; color: #cc3333; font-weight: bold; } "
                    "QGroupBox::title { subcontrol-origin: margin; left: 8px; }"
                )
                ownership_layout = QVBoxLayout(ownership_group)
                self.chk_ownership = QCheckBox(
                    "I confirm I own or am authorized to recover this volume."
                )
                self.chk_ownership.setStyleSheet("color: #cc3333; font-weight: bold;")
                ownership_layout.addWidget(self.chk_ownership)
                layout.addWidget(ownership_group)

                # Source type + container family
                type_group = QGroupBox("Source Type")
                type_layout = QVBoxLayout(type_group)

                row1 = QHBoxLayout()
                row1.addWidget(QLabel("Source:"))
                self.cmb_source_type = QComboBox()
                self.cmb_source_type.addItems([
                    "File Container",
                    "Disk/Drive Image",
                    "Already Extracted Header",
                ])
                row1.addWidget(self.cmb_source_type)
                type_layout.addLayout(row1)

                row2 = QHBoxLayout()
                row2.addWidget(QLabel("Volume type:"))
                self.cmb_family = QComboBox()
                self.cmb_family.addItems(["Unknown / not sure", "VeraCrypt", "TrueCrypt"])
                row2.addWidget(self.cmb_family)
                type_layout.addLayout(row2)

                lbl_future = QLabel(
                    "Raw Physical Disk — Future  |  Raw Physical Partition — Future"
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
                self.chk_hidden = QCheckBox("Hidden Volume Header (offset 65 536)")
                self.chk_system = QCheckBox("System Header (offset 31 744)")
                self.chk_normal.setChecked(True)
                self.chk_hidden.setChecked(True)
                self.chk_system.setChecked(False)
                extract_layout.addWidget(self.chk_normal)
                extract_layout.addWidget(self.chk_hidden)
                extract_layout.addWidget(self.chk_system)
                lbl_extract_note = QLabel(
                    "Already-Extracted Header mode: the file itself is imported as the header."
                )
                lbl_extract_note.setStyleSheet("color: gray; font-style: italic; font-size: 11px;")
                extract_layout.addWidget(lbl_extract_note)
                layout.addWidget(extract_group)

                # Connect source type to hide/show extraction options
                self.cmb_source_type.currentIndexChanged.connect(self._on_source_type_changed)
                self._on_source_type_changed(0)

                # Buttons
                buttons = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                )
                buttons.accepted.connect(self._on_accept)
                buttons.rejected.connect(self.reject)
                layout.addWidget(buttons)

            def _on_source_type_changed(self, index: int) -> None:
                is_preextracted = (index == 2)
                self.chk_normal.setEnabled(not is_preextracted)
                self.chk_hidden.setEnabled(not is_preextracted)
                self.chk_system.setEnabled(not is_preextracted)

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
                        "You must confirm ownership or authorization before adding a volume.",
                    )
                    return

                path = self.txt_path.text().strip()
                if not path:
                    QMessageBox.warning(self, "No File Selected", "Please select a source file.")
                    return

                source_idx = self.cmb_source_type.currentIndex()
                source_type_map = {
                    0: "file_container",
                    1: "disk_image",
                    2: "extracted_header",
                }
                family_map = {
                    0: "unknown",
                    1: "veracrypt",
                    2: "truecrypt",
                }

                is_preextracted = (source_idx == 2)
                self.result_data = WizardResult(
                    source_path=path,
                    source_type=source_type_map.get(source_idx, "unknown"),
                    container_family=family_map.get(self.cmb_family.currentIndex(), "unknown"),
                    extract_normal=True if is_preextracted else self.chk_normal.isChecked(),
                    extract_hidden=False if is_preextracted else self.chk_hidden.isChecked(),
                    extract_system=False if is_preextracted else self.chk_system.isChecked(),
                )
                self.accept()

        return _AddVolumeWizard(parent)
