"""Settings view — Hashcat setup, workspace, preferences."""

from __future__ import annotations


class SettingsView:  # pragma: no cover
    """Settings: Hashcat path, device scan, workspace, clipboard/queue preferences."""

    def __new__(cls, app_state=None):
        from PySide6.QtWidgets import (
            QFileDialog,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QPushButton,
            QSpinBox,
            QVBoxLayout,
            QWidget,
        )

        class _SettingsView(QWidget):
            def __init__(self, app_state=None) -> None:
                super().__init__()
                self.app_state = app_state
                layout = QVBoxLayout(self)

                # --- Hashcat Setup ---
                hc_group = QGroupBox("Hashcat Setup")
                hc_layout = QVBoxLayout(hc_group)

                path_row = QHBoxLayout()
                self.txt_hc_path = QLineEdit()
                self.txt_hc_path.setPlaceholderText("Path to hashcat or hashcat.exe...")
                self.btn_browse_hc = QPushButton("Browse...")
                self.btn_verify_hc = QPushButton("Verify")
                self.btn_scan_devices = QPushButton("Scan Devices")
                path_row.addWidget(QLabel("Hashcat:"))
                path_row.addWidget(self.txt_hc_path, 1)
                path_row.addWidget(self.btn_browse_hc)
                path_row.addWidget(self.btn_verify_hc)
                path_row.addWidget(self.btn_scan_devices)
                hc_layout.addLayout(path_row)

                self.lbl_hc_status = QLabel("Status: Not configured")
                hc_layout.addWidget(self.lbl_hc_status)
                layout.addWidget(hc_group)

                # --- Workspace ---
                ws_group = QGroupBox("Workspace")
                ws_layout = QVBoxLayout(ws_group)
                self.lbl_ws_info = QLabel("No workspace open")
                ws_path_row = QHBoxLayout()
                self.btn_create_ws = QPushButton("Create New Workspace...")
                self.btn_open_ws = QPushButton("Open Workspace...")
                ws_path_row.addWidget(self.btn_create_ws)
                ws_path_row.addWidget(self.btn_open_ws)
                ws_path_row.addStretch()
                ws_layout.addWidget(self.lbl_ws_info)
                ws_layout.addLayout(ws_path_row)
                layout.addWidget(ws_group)

                # --- Preferences ---
                pref_group = QGroupBox("Preferences")
                pref_layout = QVBoxLayout(pref_group)
                clip_row = QHBoxLayout()
                clip_row.addWidget(QLabel("Clipboard auto-clear (seconds):"))
                self.spn_clip_clear = QSpinBox()
                self.spn_clip_clear.setRange(0, 3600)
                self.spn_clip_clear.setValue(60)
                clip_row.addWidget(self.spn_clip_clear)
                clip_row.addStretch()
                pref_layout.addLayout(clip_row)
                layout.addWidget(pref_group)

                layout.addStretch()

                # Wire signals
                self.btn_browse_hc.clicked.connect(self._browse_hashcat)
                self.btn_verify_hc.clicked.connect(self._verify_hashcat)
                self.btn_scan_devices.clicked.connect(self._scan_devices)
                self.btn_create_ws.clicked.connect(self._create_workspace)
                self.btn_open_ws.clicked.connect(self._open_workspace)

                if app_state:
                    self.refresh(app_state)

            def refresh(self, app_state) -> None:
                self.app_state = app_state
                if app_state.hashcat_setup.executable_path:
                    self.txt_hc_path.setText(app_state.hashcat_setup.executable_path)
                if app_state.hashcat_setup.verified:
                    self.lbl_hc_status.setText(
                        f"Status: Verified ({app_state.hashcat_setup.version_string})"
                    )
                else:
                    self.lbl_hc_status.setText("Status: Not verified")
                if app_state.workspace_root:
                    self.lbl_ws_info.setText(
                        f"{app_state.workspace_name} — {app_state.workspace_root}"
                    )
                self.spn_clip_clear.setValue(app_state.clipboard_auto_clear_seconds)

            def _browse_hashcat(self) -> None:
                path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Select Hashcat Executable",
                    "",
                    "Executables (*.exe *.cmd *hashcat* *);;All Files (*)",
                )
                if path:
                    self.txt_hc_path.setText(path)

            def _verify_hashcat(self) -> None:
                from pathlib import Path
                from PySide6.QtWidgets import QMessageBox
                from portable_crypt_recovery.services.hashcat.verifier import verify_hashcat

                path = self.txt_hc_path.text().strip()
                if not path:
                    QMessageBox.warning(self, "No Path", "Enter a Hashcat executable path first.")
                    return
                result = verify_hashcat(Path(path))
                if result.ok:
                    self.lbl_hc_status.setText(f"Status: Verified — {result.version_text}")
                    QMessageBox.information(self, "Hashcat Verified", f"Version: {result.version_text}")
                else:
                    self.lbl_hc_status.setText(f"Status: Failed — {result.error}")
                    QMessageBox.critical(self, "Hashcat Verification Failed", str(result.error))

            def _scan_devices(self) -> None:
                from pathlib import Path
                from PySide6.QtWidgets import QMessageBox
                from portable_crypt_recovery.services.hashcat.device_scan import scan_devices

                path = self.txt_hc_path.text().strip()
                if not path:
                    QMessageBox.warning(self, "No Path", "Enter a Hashcat executable path first.")
                    return
                result = scan_devices(Path(path))
                if result.ok:
                    devices = "\n".join(
                        f"  {d.get('label', '?')}: {d.get('name', '?')}"
                        for d in result.devices
                    )
                    QMessageBox.information(self, "Devices Found", f"Detected devices:\n{devices}")
                else:
                    QMessageBox.warning(self, "Device Scan Failed", str(result.error))

            def _create_workspace(self) -> None:
                from PySide6.QtWidgets import QFileDialog, QInputDialog
                folder = QFileDialog.getExistingDirectory(self, "Choose Workspace Location")
                if not folder:
                    return
                name, ok = QInputDialog.getText(self, "Workspace Name", "Enter workspace name:")
                if not ok or not name.strip():
                    return
                from pathlib import Path
                from portable_crypt_recovery.workspace.workspace_manager import create_workspace
                ws = create_workspace(Path(folder) / name.strip(), name.strip())
                self.lbl_ws_info.setText(f"{ws.name} — {ws.root}")

            def _open_workspace(self) -> None:
                from PySide6.QtWidgets import QFileDialog, QMessageBox
                folder = QFileDialog.getExistingDirectory(self, "Select Workspace Folder")
                if not folder:
                    return
                from pathlib import Path
                from portable_crypt_recovery.workspace.workspace_manager import open_workspace
                try:
                    ws = open_workspace(Path(folder))
                    self.lbl_ws_info.setText(f"{ws.name} — {ws.root}")
                except FileNotFoundError as exc:
                    QMessageBox.critical(self, "Not a Workspace", str(exc))

        return _SettingsView(app_state)
