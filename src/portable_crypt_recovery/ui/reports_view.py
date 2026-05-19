"""Reports view — list and view generated reports."""

from __future__ import annotations


class ReportsView:  # pragma: no cover
    """List of cracked-job reports with Refresh/Export/View-Folder actions."""

    def __new__(cls, workspace_root=None):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QHBoxLayout,
            QLabel,
            QListWidget,
            QPlainTextEdit,
            QPushButton,
            QSplitter,
            QVBoxLayout,
            QWidget,
        )

        class _ReportsView(QWidget):
            def __init__(self, workspace_root=None) -> None:
                super().__init__()
                layout = QVBoxLayout(self)

                toolbar = QHBoxLayout()
                self.btn_refresh = QPushButton("Refresh")
                self.btn_copy_pw = QPushButton("Copy Password")
                self.btn_export = QPushButton("Export Report Folder...")
                self.btn_view_folder = QPushButton("Open Report Folder")
                for btn in [self.btn_refresh, self.btn_copy_pw, self.btn_export, self.btn_view_folder]:
                    toolbar.addWidget(btn)
                toolbar.addStretch()
                layout.addLayout(toolbar)

                splitter = QSplitter(Qt.Orientation.Vertical)

                self.report_list = QListWidget()
                splitter.addWidget(self.report_list)

                self.detail_pane = QPlainTextEdit()
                self.detail_pane.setReadOnly(True)
                self.detail_pane.setPlaceholderText("Select a report to view details.")
                splitter.addWidget(self.detail_pane)

                splitter.setSizes([250, 150])
                layout.addWidget(splitter, 1)

                self.lbl_count = QLabel("No reports")
                layout.addWidget(self.lbl_count)

                self.btn_refresh.clicked.connect(self.refresh)
                self.btn_copy_pw.clicked.connect(self._copy_password)
                self.btn_view_folder.clicked.connect(self._view_folder)
                self.btn_export.clicked.connect(self._export)
                self.report_list.currentRowChanged.connect(self._on_selection_changed)

                self.refresh()

            def _workspace(self):
                from portable_crypt_recovery.app.app_state import get_app_state
                state = get_app_state()
                return state.workspace_root if state.is_workspace_open() else None

            # ------------------------------------------------------------------
            # Refresh
            # ------------------------------------------------------------------

            def refresh(self) -> None:
                self.report_list.clear()
                self.detail_pane.clear()
                ws = self._workspace()
                if ws is None:
                    self.lbl_count.setText("No workspace open")
                    return

                from portable_crypt_recovery.services.reports.report_index import list_reports
                try:
                    self._reports = list_reports(ws)
                except Exception:
                    self._reports = []

                for r in self._reports:
                    cracked = r.get("cracked_password")
                    cracked_label = "CRACKED" if cracked else "no password"
                    label = (
                        f"{r.get('created_timestamp', '?')[:19]}  |  "
                        f"Task {r.get('job_id', '?')[:8]}  |  {cracked_label}"
                    )
                    self.report_list.addItem(label)

                count = len(self._reports)
                self.lbl_count.setText(f"{count} report{'s' if count != 1 else ''}")

            def _on_selection_changed(self, row: int) -> None:
                if not hasattr(self, "_reports") or row < 0 or row >= len(self._reports):
                    self.detail_pane.clear()
                    return
                r = self._reports[row]
                lines = [
                    f"Report ID:  {r.get('report_id', '?')}",
                    f"Task ID:    {r.get('job_id', '?')}",
                    f"Created:    {r.get('created_timestamp', '?')}",
                    f"Folder:     {r.get('report_folder', '?')}",
                    "",
                ]
                pw = r.get("cracked_password")
                if pw:
                    lines.append("Password recovered — see recovered-result.txt in the report folder.")
                    lines.append("(Password not displayed here for security.)")
                else:
                    lines.append("No password recovered for this report.")
                stats = r.get("stats_text", "")
                if stats:
                    lines.append("")
                    lines.append("=== Hashcat Stats ===")
                    lines.append(stats[:2000])
                self.detail_pane.setPlainText("\n".join(lines))

            # ------------------------------------------------------------------
            # Copy password to clipboard (auto-clears after configured timeout)
            # ------------------------------------------------------------------

            def _copy_password(self) -> None:
                import json

                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.core.clipboard import copy_with_auto_clear

                ws = self._workspace()
                row = self.report_list.currentRow()
                if ws is None or not hasattr(self, "_reports") or row < 0:
                    QMessageBox.information(self, "Copy Password", "Select a report first.")
                    return
                if row >= len(self._reports):
                    return

                report = self._reports[row]
                result_json = ws / report.get("report_folder", "") / "recovered-result.json"
                if not result_json.exists():
                    QMessageBox.information(
                        self, "Copy Password",
                        "No recovered-result.json found for this report.\n"
                        "The job may not have been cracked."
                    )
                    return

                try:
                    data = json.loads(result_json.read_text(encoding="utf-8"))
                    pw = data.get("cracked_password", "")
                except Exception as exc:
                    QMessageBox.critical(self, "Copy Password", f"Could not read result: {exc}")
                    return

                if not pw:
                    QMessageBox.information(self, "Copy Password", "No password found in this report.")
                    return

                state = get_app_state()
                seconds = state.clipboard_auto_clear_seconds
                copy_with_auto_clear(pw, clear_after_seconds=seconds)

                msg = "Password copied to clipboard."
                if seconds > 0:
                    msg += f"\nClipboard will be cleared in {seconds} seconds."
                QMessageBox.information(self, "Password Copied", msg)

            # ------------------------------------------------------------------
            # View folder
            # ------------------------------------------------------------------

            def _view_folder(self) -> None:
                import os
                import subprocess
                import sys
                ws = self._workspace()
                row = self.report_list.currentRow()
                if ws is None or not hasattr(self, "_reports") or row < 0:
                    return
                if row >= len(self._reports):
                    return
                folder = ws / self._reports[row].get("report_folder", "")
                if folder.exists():
                    if sys.platform == "win32":
                        os.startfile(str(folder))
                    else:
                        subprocess.Popen(["xdg-open", str(folder)])

            # ------------------------------------------------------------------
            # Export
            # ------------------------------------------------------------------

            def _export(self) -> None:
                import shutil

                from PySide6.QtWidgets import QFileDialog, QMessageBox
                ws = self._workspace()
                row = self.report_list.currentRow()
                if ws is None or not hasattr(self, "_reports") or row < 0:
                    QMessageBox.information(self, "Export", "Select a report first.")
                    return
                if row >= len(self._reports):
                    return
                report = self._reports[row]
                src_folder = ws / report.get("report_folder", "")
                if not src_folder.exists():
                    QMessageBox.warning(self, "Export", f"Report folder not found:\n{src_folder}")
                    return

                dest_dir = QFileDialog.getExistingDirectory(self, "Choose Export Destination")
                if not dest_dir:
                    return

                from pathlib import Path
                dest = Path(dest_dir) / src_folder.name
                try:
                    shutil.copytree(str(src_folder), str(dest))
                    QMessageBox.information(
                        self, "Export Complete",
                        f"Report folder copied to:\n{dest}"
                    )
                except Exception as exc:
                    QMessageBox.critical(self, "Export Failed", str(exc))

        return _ReportsView(workspace_root)
