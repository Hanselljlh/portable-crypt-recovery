"""Reports view — list generated reports."""

from __future__ import annotations


class ReportsView:  # pragma: no cover
    """List of cracked-job reports with Export/View/Regenerate actions."""

    def __new__(cls, workspace_root=None):
        from PySide6.QtWidgets import (
            QHBoxLayout,
            QListWidget,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

        class _ReportsView(QWidget):
            def __init__(self, workspace_root=None) -> None:
                super().__init__()
                self.workspace_root = workspace_root
                layout = QVBoxLayout(self)

                toolbar = QHBoxLayout()
                self.btn_refresh = QPushButton("Refresh")
                self.btn_export = QPushButton("Export")
                self.btn_view_folder = QPushButton("View Recovery Folder")
                self.btn_regenerate = QPushButton("Regenerate")
                for btn in [self.btn_refresh, self.btn_export, self.btn_view_folder, self.btn_regenerate]:
                    toolbar.addWidget(btn)
                toolbar.addStretch()
                layout.addLayout(toolbar)

                self.report_list = QListWidget()
                layout.addWidget(self.report_list, 1)

                self.btn_refresh.clicked.connect(self.refresh)
                self.btn_view_folder.clicked.connect(self._view_folder)
                self.btn_export.clicked.connect(self._export)
                self.btn_regenerate.clicked.connect(self._regenerate)

                self.refresh()

            def refresh(self) -> None:
                self.report_list.clear()
                if self.workspace_root is None:
                    return
                from portable_crypt_recovery.services.reports.report_index import list_reports
                try:
                    reports = list_reports(self.workspace_root)
                    for r in reports:
                        self.report_list.addItem(
                            f"{r.get('report_id', '?')} — Job {r.get('job_id', '?')} — "
                            f"{r.get('created_timestamp', '?')}"
                        )
                except Exception:
                    pass

            def _view_folder(self) -> None:
                import os
                import subprocess
                import sys
                item = self.report_list.currentItem()
                if item is None or self.workspace_root is None:
                    return
                from portable_crypt_recovery.services.reports.report_index import list_reports
                reports = list_reports(self.workspace_root)
                idx = self.report_list.currentRow()
                if 0 <= idx < len(reports):
                    folder = self.workspace_root / reports[idx].get("report_folder", "")
                    if folder.exists():
                        if sys.platform == "win32":
                            os.startfile(str(folder))
                        else:
                            subprocess.Popen(["xdg-open", str(folder)])

            def _export(self) -> None:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Export", "Select a report to export.")

            def _regenerate(self) -> None:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Regenerate", "Regeneration requires the original job data.")

        return _ReportsView(workspace_root)
