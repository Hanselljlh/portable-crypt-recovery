"""Setup view — workspace, tools, and device status at a glance."""

from __future__ import annotations


class SetupView:  # pragma: no cover
    """Quick-status screen shown as the first nav item.

    Shows workspace path, Hashcat path/version, and detected compute devices.
    All fields are read-only; the Open/Configure buttons deep-link to Settings.
    """

    def __new__(cls):
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import (
            QFormLayout,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

        class _SetupView(QWidget):
            def __init__(self) -> None:
                super().__init__()
                layout = QVBoxLayout(self)

                heading = QLabel("<b>Setup</b> — workspace, tools, and device status")
                heading.setWordWrap(True)
                layout.addWidget(heading)

                # ---- Workspace group ----
                ws_group = QGroupBox("Workspace")
                ws_form = QFormLayout(ws_group)
                self.lbl_ws_status = QLabel("No workspace open")
                self.lbl_ws_path = QLabel("—")
                self.lbl_ws_path.setWordWrap(True)
                ws_form.addRow("Status:", self.lbl_ws_status)
                ws_form.addRow("Path:", self.lbl_ws_path)

                ws_btn_row = QHBoxLayout()
                self.btn_open_ws = QPushButton("Open / Change Workspace…")
                self.btn_open_ws.clicked.connect(self._go_to_settings)
                ws_btn_row.addWidget(self.btn_open_ws)
                ws_btn_row.addStretch()
                ws_form.addRow(ws_btn_row)
                layout.addWidget(ws_group)

                # ---- Hashcat group ----
                hc_group = QGroupBox("Hashcat")
                hc_form = QFormLayout(hc_group)
                self.lbl_hc_status = QLabel("Not configured")
                self.lbl_hc_path = QLabel("—")
                self.lbl_hc_path.setWordWrap(True)
                self.lbl_hc_version = QLabel("—")
                hc_form.addRow("Status:", self.lbl_hc_status)
                hc_form.addRow("Path:", self.lbl_hc_path)
                hc_form.addRow("Version:", self.lbl_hc_version)

                hc_btn_row = QHBoxLayout()
                self.btn_configure_hc = QPushButton("Configure Hashcat…")
                self.btn_configure_hc.clicked.connect(self._go_to_settings)
                hc_btn_row.addWidget(self.btn_configure_hc)
                hc_btn_row.addStretch()
                hc_form.addRow(hc_btn_row)
                layout.addWidget(hc_group)

                # ---- Compute devices group ----
                dev_group = QGroupBox("Compute Devices")
                dev_form = QFormLayout(dev_group)
                self.lbl_device_ids = QLabel("—")
                self.lbl_device_ids.setWordWrap(True)
                dev_form.addRow("Selected device ID(s):", self.lbl_device_ids)

                dev_btn_row = QHBoxLayout()
                self.btn_configure_dev = QPushButton("Change Device Settings…")
                self.btn_configure_dev.clicked.connect(self._go_to_settings)
                dev_btn_row.addWidget(self.btn_configure_dev)
                dev_btn_row.addStretch()
                dev_form.addRow(dev_btn_row)
                layout.addWidget(dev_group)

                layout.addStretch()

                # Auto-refresh every 5 s so status stays current
                self._timer = QTimer(self)
                self._timer.setInterval(5000)
                self._timer.timeout.connect(self._refresh)
                self._timer.start()

                self._refresh()

            # ------------------------------------------------------------------

            def _refresh(self) -> None:
                """Pull current state and update all labels."""
                from portable_crypt_recovery.app.app_state import get_app_state
                state = get_app_state()

                # Workspace
                if state.is_workspace_open() and state.workspace_root:
                    self.lbl_ws_status.setText("Open")
                    self.lbl_ws_status.setStyleSheet("color: green;")
                    self.lbl_ws_path.setText(str(state.workspace_root))
                else:
                    self.lbl_ws_status.setText("Not open")
                    self.lbl_ws_status.setStyleSheet("color: #c00;")
                    self.lbl_ws_path.setText("—")

                # Hashcat
                hs = state.hashcat_setup
                hc_exe = hs.executable_path or ""
                if hc_exe:
                    self.lbl_hc_status.setText("Configured")
                    self.lbl_hc_status.setStyleSheet("color: green;")
                    self.lbl_hc_path.setText(hc_exe)
                    self.lbl_hc_version.setText(hs.version_string or "unknown")
                else:
                    self.lbl_hc_status.setText("Not configured")
                    self.lbl_hc_status.setStyleSheet("color: #c00;")
                    self.lbl_hc_path.setText("—")
                    self.lbl_hc_version.setText("—")

                # Devices
                ids = hs.selected_device_ids
                if ids:
                    self.lbl_device_ids.setText(", ".join(str(d) for d in ids))
                else:
                    self.lbl_device_ids.setText("None selected (will use Hashcat default)")

            def _refresh_list(self) -> None:
                """Called by main_window nav change — refresh status."""
                self._refresh()

            def _go_to_settings(self) -> None:
                from portable_crypt_recovery.ui.main_window import SCREEN_NAMES
                main_win = self.window()
                if hasattr(main_win, "nav"):
                    try:
                        idx = list(SCREEN_NAMES).index("Settings")
                        main_win.nav.setCurrentRow(idx)
                    except ValueError:
                        pass

        return _SetupView()
