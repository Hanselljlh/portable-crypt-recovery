"""Settings view — Hashcat setup, workspace, preferences."""

from __future__ import annotations


class SettingsView:  # pragma: no cover
    """Settings: Hashcat path, device scan, workspace, clipboard/queue preferences."""

    def __new__(cls):
        from PySide6.QtCore import QObject, QThread, Signal
        from PySide6.QtWidgets import (
            QCheckBox,
            QComboBox,
            QDialog,
            QDialogButtonBox,
            QFileDialog,
            QGroupBox,
            QHBoxLayout,
            QInputDialog,
            QLabel,
            QLineEdit,
            QPushButton,
            QSpinBox,
            QVBoxLayout,
            QWidget,
        )

        # ── background worker for verify ───────────────────────────────────
        class _VerifyWorker(QObject):
            finished = Signal(object)   # HashcatVerificationResult

            def __init__(self, path):
                super().__init__()
                self._path = path

            def run(self):
                from pathlib import Path

                from portable_crypt_recovery.services.hashcat.verifier import verify_hashcat
                self.finished.emit(verify_hashcat(Path(self._path)))

        # ── background worker for device scan ──────────────────────────────
        class _ScanWorker(QObject):
            finished = Signal(object)   # DeviceScanResult

            def __init__(self, path):
                super().__init__()
                self._path = path

            def run(self):
                from pathlib import Path

                from portable_crypt_recovery.services.hashcat.device_scan import scan_devices
                self.finished.emit(scan_devices(Path(self._path)))

        # ── background worker for backend info (driver check) ──────────────
        class _BackendInfoWorker(QObject):
            finished = Signal(str)   # raw backend-info stdout

            def __init__(self, path):
                super().__init__()
                self._path = path

            def run(self):
                import subprocess
                try:
                    r = subprocess.run(
                        [self._path, "--backend-info"],
                        capture_output=True, text=True, timeout=30
                    )
                    self.finished.emit(r.stdout + r.stderr)
                except Exception as exc:
                    self.finished.emit(f"(error running hashcat --backend-info: {exc})")

        # ── driver check dialog ────────────────────────────────────────────
        _DRIVER_ROWS = [
            {
                "hardware": "NVIDIA GPU",
                "backend": "CUDA",
                "detect_keywords": ["cuda"],
                "miss_keywords": ["cuda.version.: n/a", "no cuda", "cuda not available"],
                "description": "GeForce, RTX, Quadro — fastest option by far",
                "url": "https://developer.nvidia.com/cuda-downloads",
                "url_label": "CUDA Toolkit Downloads",
            },
            {
                "hardware": "AMD GPU",
                "backend": "HIP / OpenCL",
                "detect_keywords": ["hip", "amd", "radeon"],
                "miss_keywords": [],
                "description": "Radeon RX series — very fast; needs Adrenalin drivers",
                "url": "https://www.amd.com/en/support/download/drivers.html",
                "url_label": "amd.com/support",
            },
            {
                "hardware": "Intel GPU",
                "backend": "OpenCL",
                "detect_keywords": ["intel", "arc", "xe"],
                "miss_keywords": [],
                "description": "Arc / Xe / UHD — needs Intel GPU driver or oneAPI",
                "url": "https://www.intel.com/content/www/us/en/download-center/home.html",
                "url_label": "intel.com/download-center",
            },
            {
                "hardware": "CPU (OpenCL)",
                "backend": "OpenCL",
                "detect_keywords": ["cpu"],
                "miss_keywords": [],
                "description": "Fallback if no GPU — slow for VeraCrypt; needs OpenCL CPU runtime",
                "url": "https://github.com/intel/compute-runtime/releases",
                "url_label": "intel compute-runtime (GitHub)",
            },
        ]

        class _DriverCheckDialog(QDialog):
            def __init__(self, backend_text: str, parent=None):
                super().__init__(parent)
                from PySide6.QtGui import QDesktopServices
                from PySide6.QtWidgets import QPlainTextEdit
                self.setWindowTitle("Driver / Runtime Check")
                self.resize(700, 600)
                lay = QVBoxLayout(self)

                # --- Status grid ---
                lay.addWidget(QLabel(
                    "<b>Detected Compute Backends</b> — green = found in hashcat output, "
                    "orange = not detected (may still work if driver is installed)"
                ))
                lower = backend_text.lower()

                grid_widget = QWidget()
                grid_lay = QVBoxLayout(grid_widget)
                grid_lay.setSpacing(4)

                for row in _DRIVER_ROWS:
                    detected = any(kw in lower for kw in row["detect_keywords"])
                    missed = any(kw in lower for kw in row["miss_keywords"])
                    if detected and not missed:
                        icon = "✅"
                        color = "#2a5a2a"
                        status = "Detected"
                    else:
                        icon = "⚠"
                        color = "#5a4a00"
                        status = "Not detected"

                    row_w = QWidget()
                    row_w.setStyleSheet(f"background: {color}; border-radius: 4px;")
                    row_lay = QHBoxLayout(row_w)
                    row_lay.setContentsMargins(8, 4, 8, 4)

                    lbl_status = QLabel(f"{icon}  <b>{row['hardware']}</b>  ({row['backend']}) — {status}")
                    lbl_status.setStyleSheet("color: #e0e0e0; background: transparent;")
                    lbl_desc = QLabel(row["description"])
                    lbl_desc.setStyleSheet("color: #aaaaaa; background: transparent; font-size: 11px;")
                    btn_link = QPushButton(f"⬇ {row['url_label']}")
                    btn_link.setFlat(True)
                    btn_link.setStyleSheet(
                        "color: #6ab0f5; text-decoration: underline; "
                        "background: transparent; border: none;"
                    )
                    _url = row["url"]
                    btn_link.clicked.connect(
                        lambda checked=False, u=_url: QDesktopServices.openUrl(
                            __import__("PySide6.QtCore", fromlist=["QUrl"]).QUrl(u)
                        )
                    )

                    col_left = QVBoxLayout()
                    col_left.addWidget(lbl_status)
                    col_left.addWidget(lbl_desc)
                    row_lay.addLayout(col_left, 1)
                    row_lay.addWidget(btn_link)
                    grid_lay.addWidget(row_w)

                lay.addWidget(grid_widget)

                # --- Raw backend info ---
                lay.addWidget(QLabel("<b>Raw hashcat --backend-info output:</b>"))
                txt = QPlainTextEdit()
                txt.setReadOnly(True)
                txt.setPlainText(backend_text if backend_text.strip()
                                 else "(no output — is hashcat verified?)")
                txt.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
                lay.addWidget(txt, 1)

                close_btn = QPushButton("Close")
                close_btn.clicked.connect(self.accept)
                lay.addWidget(close_btn)

        # ── device selection dialog ────────────────────────────────────────
        class _DeviceDialog(QDialog):
            def __init__(self, devices, current_ids, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Select Compute Devices")
                self.resize(480, 320)
                lay = QVBoxLayout(self)
                lay.addWidget(QLabel("Choose which devices Hashcat should use:"))
                self._checks = []
                for i, dev in enumerate(devices):
                    label = f"{dev.get('label', f'Device {i}')}  —  {dev.get('name', '?')}"
                    cb = QCheckBox(label)
                    cb.setChecked(i in current_ids or not current_ids)
                    cb.setProperty("device_index", str(i))
                    lay.addWidget(cb)
                    self._checks.append(cb)
                if not devices:
                    lay.addWidget(QLabel("No devices detected. Check Hashcat output."))
                btns = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                )
                btns.accepted.connect(self.accept)
                btns.rejected.connect(self.reject)
                lay.addWidget(btns)

            def selected_ids(self) -> list[int]:
                return [
                    int(cb.property("device_index"))
                    for cb in self._checks
                    if cb.isChecked()
                ]

        # ── main view ─────────────────────────────────────────────────────
        class _SettingsView(QWidget):
            def __init__(self) -> None:
                super().__init__()
                self._thread = None
                self._worker = None
                layout = QVBoxLayout(self)

                # ── Hashcat Setup ─────────────────────────────────────────
                hc_group = QGroupBox("Hashcat Setup")
                hc_layout = QVBoxLayout(hc_group)

                # Status label (prominent)
                self.lbl_hc_status = QLabel("Status: Not configured")
                self.lbl_hc_status.setStyleSheet("font-weight: bold;")
                hc_layout.addWidget(self.lbl_hc_status)

                # Path row
                path_row = QHBoxLayout()
                path_row.addWidget(QLabel("Executable:"))
                self.txt_hc_path = QLineEdit()
                self.txt_hc_path.setPlaceholderText("Path to hashcat or hashcat.exe…")
                path_row.addWidget(self.txt_hc_path, 1)
                self.btn_browse_hc = QPushButton("Browse…")
                path_row.addWidget(self.btn_browse_hc)
                hc_layout.addLayout(path_row)

                # Action buttons row
                btn_row = QHBoxLayout()
                self.btn_portable_tools = QPushButton("Use Portable Tools Folder")
                self.btn_verify_hc = QPushButton("Verify Hashcat")
                self.btn_scan_devices = QPushButton("Scan Devices")
                self.btn_driver_check = QPushButton("Driver / Runtime Check…")
                self.btn_download_page = QPushButton("Open Hashcat Download Page")
                btn_row.addWidget(self.btn_portable_tools)
                btn_row.addWidget(self.btn_verify_hc)
                btn_row.addWidget(self.btn_scan_devices)
                btn_row.addWidget(self.btn_driver_check)
                btn_row.addWidget(self.btn_download_page)
                btn_row.addStretch()
                hc_layout.addLayout(btn_row)

                # Detected version + devices
                self.lbl_hc_version = QLabel("Version: —")
                self.lbl_hc_devices = QLabel("Devices: —")
                hc_layout.addWidget(self.lbl_hc_version)
                hc_layout.addWidget(self.lbl_hc_devices)

                # Performance flags
                self.chk_optimized_kernels = QCheckBox(
                    "Optimized kernels  (-O)  —  2-4× faster; limits passwords to ≤31 characters"
                )
                self.chk_optimized_kernels.setChecked(True)
                self.chk_optimized_kernels.setToolTip(
                    "Enables hashcat's -O flag (--optimized-kernel-enable).\n"
                    "Uses SIMD-optimized code paths for significantly higher hash-rates.\n"
                    "Passwords longer than ~31 characters will NOT be found when this is on.\n"
                    "Uncheck if you believe the password exceeds 31 characters."
                )
                hc_layout.addWidget(self.chk_optimized_kernels)

                self.chk_cpu_opencl = QCheckBox(
                    "CPU OpenCL  (-D 1)  —  3-5× faster on CPU; requires Intel or AMD OpenCL runtime"
                )
                self.chk_cpu_opencl.setChecked(False)
                self.chk_cpu_opencl.setToolTip(
                    "Adds -D 1 so hashcat uses the OpenCL CPU backend instead of its\n"
                    "built-in pure-CPU path. Can be 3-5× faster when the Intel OpenCL\n"
                    "Runtime or AMD APP SDK is installed.\n\n"
                    "Leave OFF if you have not installed a CPU OpenCL runtime — hashcat\n"
                    "will error on startup if the runtime is missing."
                )
                hc_layout.addWidget(self.chk_cpu_opencl)

                self.chk_ignore_cuda = QCheckBox(
                    "Ignore CUDA  (--backend-ignore-cuda)  —  skip CUDA; fall back to CPU"
                )
                self.chk_ignore_cuda.setChecked(False)
                self.chk_ignore_cuda.setToolTip(
                    "Adds --backend-ignore-cuda so hashcat skips the CUDA backend\n"
                    "entirely and falls back to OpenCL or the built-in CPU backend.\n\n"
                    "Enable this if you see:\n"
                    "  'Unsupported .version X.Y; current version is A.B'\n"
                    "in your job logs. This error means your NVIDIA driver is too old\n"
                    "for this version of hashcat (driver 570+ required for hashcat 7.x).\n\n"
                    "Jobs will run on CPU — much slower, but correct results."
                )
                hc_layout.addWidget(self.chk_ignore_cuda)

                self.btn_save_hc_perf = QPushButton("Save Performance Settings")
                hc_layout.addWidget(self.btn_save_hc_perf)

                layout.addWidget(hc_group)

                # ── Workspace ─────────────────────────────────────────────
                ws_group = QGroupBox("Workspace")
                ws_layout = QVBoxLayout(ws_group)
                self.lbl_ws_info = QLabel("No workspace open")
                self.lbl_ws_info.setWordWrap(True)
                ws_layout.addWidget(self.lbl_ws_info)
                ws_btn_row = QHBoxLayout()
                self.btn_create_ws = QPushButton("Create New Workspace…")
                self.btn_open_ws = QPushButton("Open Workspace…")
                ws_btn_row.addWidget(self.btn_create_ws)
                ws_btn_row.addWidget(self.btn_open_ws)
                ws_btn_row.addStretch()
                ws_layout.addLayout(ws_btn_row)
                layout.addWidget(ws_group)

                # ── Preferences ───────────────────────────────────────────
                pref_group = QGroupBox("Preferences")
                pref_layout = QVBoxLayout(pref_group)

                clip_row = QHBoxLayout()
                clip_row.addWidget(QLabel("Clipboard auto-clear after copying password (seconds, 0 = disabled):"))
                self.spn_clip_clear = QSpinBox()
                self.spn_clip_clear.setRange(0, 3600)
                self.spn_clip_clear.setValue(60)
                clip_row.addWidget(self.spn_clip_clear)
                clip_row.addStretch()
                pref_layout.addLayout(clip_row)

                crack_row = QHBoxLayout()
                crack_row.addWidget(QLabel("After a target is cracked:"))
                self.cmb_crack_behavior = QComboBox()
                self.cmb_crack_behavior.addItems([
                    "Continue with other uncracked targets",
                    "Stop the entire queue",
                ])
                crack_row.addWidget(self.cmb_crack_behavior)
                crack_row.addStretch()
                pref_layout.addLayout(crack_row)

                self.btn_save_prefs = QPushButton("Save Preferences")
                pref_layout.addWidget(self.btn_save_prefs)
                layout.addWidget(pref_group)

                layout.addStretch()

                # ── Wire signals ──────────────────────────────────────────
                self.btn_browse_hc.clicked.connect(self._browse_hashcat)
                self.btn_portable_tools.clicked.connect(self._use_portable_tools)
                self.btn_verify_hc.clicked.connect(self._verify_hashcat)
                self.btn_scan_devices.clicked.connect(self._scan_devices)
                self.btn_driver_check.clicked.connect(self._driver_check)
                self.btn_download_page.clicked.connect(self._open_download_page)
                self.btn_save_hc_perf.clicked.connect(self._save_hc_perf)
                self.btn_create_ws.clicked.connect(self._create_workspace)
                self.btn_open_ws.clicked.connect(self._open_workspace)
                self.btn_save_prefs.clicked.connect(self._save_preferences)

                self._refresh_from_state()

            # ── helpers ───────────────────────────────────────────────────

            def _state(self):
                from portable_crypt_recovery.app.app_state import get_app_state
                return get_app_state()

            def _refresh_from_state(self):
                state = self._state()
                hc = state.hashcat_setup
                if hc.executable_path:
                    self.txt_hc_path.setText(str(hc.executable_path))
                if hc.verified and hc.version_string:
                    self.lbl_hc_status.setText("Status: ✓ Verified")
                    self.lbl_hc_status.setStyleSheet("font-weight: bold; color: green;")
                    self.lbl_hc_version.setText(f"Version: {hc.version_string}")
                else:
                    self.lbl_hc_status.setText("Status: Not configured — browse to hashcat and click Verify")
                    self.lbl_hc_status.setStyleSheet("font-weight: bold; color: #cc4400;")
                if hc.selected_device_ids:
                    self.lbl_hc_devices.setText(
                        f"Selected devices: {', '.join(str(d) for d in hc.selected_device_ids)}"
                    )
                self.chk_optimized_kernels.setChecked(hc.use_optimized_kernels)
                self.chk_cpu_opencl.setChecked(hc.use_cpu_opencl)
                self.chk_ignore_cuda.setChecked(hc.ignore_cuda)
                if state.workspace_root:
                    self.lbl_ws_info.setText(
                        f"{state.workspace_name}\n{state.workspace_root}"
                    )
                self.spn_clip_clear.setValue(state.clipboard_auto_clear_seconds)
                behavior = state.queue_behavior_after_crack
                self.cmb_crack_behavior.setCurrentIndex(
                    0 if "continue" in behavior else 1
                )

            def _save_hc_perf(self):
                """Save performance settings (optimized kernels toggle)."""
                import json

                from PySide6.QtWidgets import QMessageBox
                state = self._state()
                hc = state.hashcat_setup
                hc.use_optimized_kernels = self.chk_optimized_kernels.isChecked()
                hc.use_cpu_opencl = self.chk_cpu_opencl.isChecked()
                hc.ignore_cuda = self.chk_ignore_cuda.isChecked()
                if state.workspace_root:
                    settings_path = state.workspace_root / "settings.json"
                    try:
                        data = json.loads(settings_path.read_text(encoding="utf-8"))
                    except Exception:
                        data = {"schema_version": 1}
                    data["use_optimized_kernels"] = hc.use_optimized_kernels
                    data["use_cpu_opencl"] = hc.use_cpu_opencl
                    data["ignore_cuda"] = hc.ignore_cuda
                    from portable_crypt_recovery.core.atomic_write import atomic_write_json
                    atomic_write_json(settings_path, data)
                flag = "ON  (-O active)" if hc.use_optimized_kernels else "OFF (no -O, max password length unlimited)"
                cpu_flag = "ON  (-D 1 active)" if hc.use_cpu_opencl else "OFF"
                cuda_flag = "ON  (--backend-ignore-cuda active)" if hc.ignore_cuda else "OFF"
                QMessageBox.information(
                    self, "Saved",
                    f"Optimized kernels: {flag}\n"
                    f"CPU OpenCL: {cpu_flag}\n"
                    f"Ignore CUDA: {cuda_flag}\n\n"
                    "Takes effect on the next Start Queue."
                )

            def _persist_hashcat_settings(self):
                """Write hashcat path + devices to workspace settings.json."""
                import json
                state = self._state()
                if not state.workspace_root:
                    return
                settings_path = state.workspace_root / "settings.json"
                try:
                    data = json.loads(settings_path.read_text(encoding="utf-8"))
                except Exception:
                    data = {"schema_version": 1}
                hc = state.hashcat_setup
                data["hashcat_path"] = str(hc.executable_path) if hc.executable_path else None
                data["hashcat_verified"] = hc.verified
                data["hashcat_version"] = hc.version_string
                data["selected_device_ids"] = hc.selected_device_ids
                data["use_optimized_kernels"] = hc.use_optimized_kernels
                data["use_cpu_opencl"] = hc.use_cpu_opencl
                data["ignore_cuda"] = hc.ignore_cuda
                from portable_crypt_recovery.core.atomic_write import atomic_write_json
                atomic_write_json(settings_path, data)

            # ── Hashcat actions ───────────────────────────────────────────

            def _browse_hashcat(self):
                path, _ = QFileDialog.getOpenFileName(
                    self, "Select Hashcat Executable", "",
                    "Executables (hashcat hashcat.exe hashcat.bin *.exe);;All Files (*.*)",
                )
                if path:
                    self.txt_hc_path.setText(path)

            def _use_portable_tools(self):
                from portable_crypt_recovery.core.paths import app_root_from_cwd
                from portable_crypt_recovery.services.hashcat.locator import find_in_portable_tools
                found = find_in_portable_tools(app_root_from_cwd())
                if found:
                    self.txt_hc_path.setText(str(found))
                    # File is confirmed present — verify immediately
                    self._verify_hashcat()
                else:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self, "Not Found",
                        "Hashcat was not found in the portable tools folder.\n\n"
                        "Place hashcat.exe (Windows) or hashcat (Linux) in:\n"
                        "  PCR/tools/hashcat/\n\n"
                        "Or click Browse to locate an existing Hashcat executable.",
                    )

            def _verify_hashcat(self):
                path = self.txt_hc_path.text().strip()
                if not path:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "No Path", "Enter or browse to the Hashcat executable first.")
                    return
                self._set_busy(True, "Verifying…")
                self._run_in_thread(_VerifyWorker(path), self._on_verify_done)

            def _on_verify_done(self, result):
                self._set_busy(False)
                state = self._state()
                hc = state.hashcat_setup
                if result.ok:
                    hc.executable_path = str(result.executable_path)
                    hc.verified = True
                    hc.version_string = result.version_text or ""
                    self.lbl_hc_status.setText("Status: ✓ Verified")
                    self.lbl_hc_status.setStyleSheet("font-weight: bold; color: green;")
                    self.lbl_hc_version.setText(f"Version: {hc.version_string}")
                    self._persist_hashcat_settings()
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self, "Hashcat Verified",
                        f"Version: {hc.version_string}\n\nClick 'Scan Devices' to detect compute devices.",
                    )
                else:
                    hc.verified = False
                    self.lbl_hc_status.setText("Status: ✗ Verification failed")
                    self.lbl_hc_status.setStyleSheet("font-weight: bold; color: red;")
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.critical(
                        self, "Verification Failed",
                        f"{result.error}\n\n"
                        "Check that the selected file is the real Hashcat executable.",
                    )

            def _driver_check(self):
                path = self.txt_hc_path.text().strip()
                if not path:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        self, "No Path",
                        "Verify Hashcat first so the executable path is known."
                    )
                    return
                self._set_busy(True, "Running hashcat --backend-info…")
                self._run_in_thread(_BackendInfoWorker(path), self._on_driver_check_done)

            def _on_driver_check_done(self, backend_text: str):
                self._set_busy(False)
                dlg = _DriverCheckDialog(backend_text, self)
                dlg.exec()

            def _scan_devices(self):
                path = self.txt_hc_path.text().strip()
                if not path:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "No Path", "Verify Hashcat first.")
                    return
                self._set_busy(True, "Scanning devices…")
                self._run_in_thread(_ScanWorker(path), self._on_scan_done)

            def _on_scan_done(self, result):
                self._set_busy(False)
                state = self._state()
                if not result.ok and not result.devices:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        self, "Scan Failed",
                        f"Could not scan devices.\n\n{result.error or ''}\n\n"
                        "Install or update your GPU/CPU compute runtime and try again.",
                    )
                    return
                dlg = _DeviceDialog(result.devices, state.hashcat_setup.selected_device_ids, self)
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    ids = dlg.selected_ids()  # list[int] after fix
                    state.hashcat_setup.selected_device_ids = ids
                    self.lbl_hc_devices.setText(
                        f"Selected devices: {', '.join(str(i) for i in ids)}"
                        if ids else "No devices selected"
                    )
                    self._persist_hashcat_settings()

            def _open_download_page(self):
                from PySide6.QtCore import QUrl
                from PySide6.QtGui import QDesktopServices
                QDesktopServices.openUrl(QUrl("https://hashcat.net/hashcat/"))

            # ── Workspace actions ─────────────────────────────────────────

            def _create_workspace(self):
                folder = QFileDialog.getExistingDirectory(self, "Choose Location for New Workspace")
                if not folder:
                    return
                name, ok = QInputDialog.getText(
                    self, "Workspace Name", "Enter a name for the workspace:"
                )
                if not ok or not name.strip():
                    return
                from pathlib import Path

                from portable_crypt_recovery.workspace.workspace_manager import create_workspace
                ws_root = Path(folder) / name.strip()
                ws = create_workspace(ws_root, name.strip())
                self._activate_workspace(ws)

            def _open_workspace(self):
                folder = QFileDialog.getExistingDirectory(self, "Select Workspace Folder")
                if not folder:
                    return
                from pathlib import Path

                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.workspace.workspace_manager import open_workspace
                try:
                    ws = open_workspace(Path(folder))
                    self._activate_workspace(ws)
                except FileNotFoundError as exc:
                    QMessageBox.critical(self, "Not a Workspace", str(exc))

            def _activate_workspace(self, ws):
                """Populate app_state from a just-opened or just-created workspace."""
                import json
                state = self._state()
                state.load_from_workspace(ws.root, ws.record)

                # Load settings.json into app_state
                settings_path = ws.root / "settings.json"
                if settings_path.exists():
                    try:
                        settings = json.loads(settings_path.read_text(encoding="utf-8"))
                        state.load_settings(settings)
                        hc_path = settings.get("hashcat_path")
                        if hc_path:
                            state.hashcat_setup.executable_path = hc_path
                            state.hashcat_setup.verified = settings.get("hashcat_verified", False)
                            state.hashcat_setup.version_string = settings.get("hashcat_version", "")
                            # Load device IDs: canonical key first, legacy fallback
                            raw_ids = (
                                settings.get("selected_device_ids")
                                or settings.get("selected_compute_devices")
                                or []
                            )
                            state.hashcat_setup.selected_device_ids = [int(d) for d in raw_ids]
                    except Exception:
                        pass

                # Refresh counts
                self._refresh_counts(state, ws.root)
                self.lbl_ws_info.setText(f"{ws.name}\n{ws.root}")
                self._refresh_from_state()

                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self, "Workspace Opened",
                    f"Workspace '{ws.name}' is now active.\n{ws.root}",
                )

            def _refresh_counts(self, state, workspace_root):
                import json
                try:
                    targets_file = workspace_root / "targets" / "targets.json"
                    data = json.loads(targets_file.read_text(encoding="utf-8"))
                    state.target_count = len(data.get("targets", []))
                except Exception:
                    state.target_count = 0
                try:
                    from portable_crypt_recovery.services.headers.metadata import list_header_ids
                    state.header_count = len(list_header_ids(workspace_root))
                except Exception:
                    state.header_count = 0
                try:
                    queue_file = workspace_root / "queue" / "queue-state.json"
                    if queue_file.exists():
                        qs_data = json.loads(queue_file.read_text(encoding="utf-8"))
                        state.job_count = len(qs_data.get("jobs", {}))
                    else:
                        state.job_count = 0
                except Exception:
                    state.job_count = 0

            # ── Preferences ───────────────────────────────────────────────

            def _save_preferences(self):
                import json
                state = self._state()
                state.clipboard_auto_clear_seconds = self.spn_clip_clear.value()
                idx = self.cmb_crack_behavior.currentIndex()
                state.queue_behavior_after_crack = (
                    "continue_other_uncracked_targets" if idx == 0 else "stop_entire_queue"
                )
                if state.workspace_root:
                    settings_path = state.workspace_root / "settings.json"
                    try:
                        data = json.loads(settings_path.read_text(encoding="utf-8"))
                    except Exception:
                        data = {"schema_version": 1}
                    data["clipboard_auto_clear_seconds"] = state.clipboard_auto_clear_seconds
                    data["default_queue_behavior_after_crack"] = state.queue_behavior_after_crack
                    from portable_crypt_recovery.core.atomic_write import atomic_write_json
                    atomic_write_json(settings_path, data)
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self, "Saved", "Preferences saved to workspace settings."
                    )
                else:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self, "Saved",
                        "Preferences saved for this session.\nOpen a workspace to persist them."
                    )

            # ── threading helper ──────────────────────────────────────────

            def _set_busy(self, busy: bool, label: str = ""):
                self.btn_verify_hc.setEnabled(not busy)
                self.btn_scan_devices.setEnabled(not busy)
                self.btn_driver_check.setEnabled(not busy)
                self.btn_browse_hc.setEnabled(not busy)
                if busy and label:
                    self.lbl_hc_status.setText(f"Status: {label}")
                    self.lbl_hc_status.setStyleSheet("font-weight: bold; color: #555;")

            def _run_in_thread(self, worker, callback):
                thread = QThread(self)
                worker.moveToThread(thread)
                worker.finished.connect(callback)
                worker.finished.connect(thread.quit)
                thread.started.connect(worker.run)
                thread.finished.connect(thread.deleteLater)
                # Keep references alive
                self._thread = thread
                self._worker = worker
                thread.start()

        return _SettingsView()
