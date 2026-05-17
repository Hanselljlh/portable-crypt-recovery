"""Workspace Cleanup view — bulk-delete intermediate recovery files."""

from __future__ import annotations


# Categories the user can choose to delete.
# Each entry: (label, workspace-relative glob patterns, safe_to_delete_note)
_CATEGORIES = [
    (
        "Hashcat potfiles",
        ["hashcat/potfile"],
        "Contain cracked hashes. Safe to delete after securing recovery packages.",
    ),
    (
        "Hashcat restore files",
        ["hashcat/restore"],
        "Session state for resuming jobs. Safe to delete if you won't resume.",
    ),
    (
        "Hashcat output files",
        ["hashcat/output"],
        "Raw outfile lines written by Hashcat. Covered by reports.",
    ),
    (
        "Generated wordlists",
        ["generated/wordlists"],
        "Auto-generated wordlist files. Original source wordlists are not deleted.",
    ),
    (
        "Generated PIM lists",
        ["generated/pim-lists"],
        "Auto-generated PIM range files.",
    ),
    (
        "Normalized headers",
        ["headers/normalized"],
        "512-byte header copies used as Hashcat input. Keep recovery packages first.",
    ),
    (
        "Normalized keyfiles",
        ["inputs/keyfiles/normalized"],
        "Keyfile copies. Originals are not touched.",
    ),
    (
        "Workspace logs",
        ["logs"],
        "App and queue log files.",
    ),
]


class CleanupView:  # pragma: no cover
    """Workspace cleanup — shows disk usage per category and deletes selected ones."""

    def __new__(cls):
        import shutil
        from pathlib import Path

        from PySide6.QtCore import Qt, QThread, Signal, QObject
        from PySide6.QtWidgets import (
            QAbstractItemView,
            QGroupBox,
            QHBoxLayout,
            QHeaderView,
            QLabel,
            QMessageBox,
            QPushButton,
            QTableWidget,
            QTableWidgetItem,
            QVBoxLayout,
            QWidget,
        )

        class _SizeWorker(QObject):
            finished = Signal(list)   # list of (label, size_bytes)

            def __init__(self, workspace_root: Path) -> None:
                super().__init__()
                self._root = workspace_root

            def run(self) -> None:
                results = []
                for label, paths, _ in _CATEGORIES:
                    total = 0
                    for rel in paths:
                        d = self._root / rel
                        if d.exists():
                            for f in d.rglob("*"):
                                if f.is_file():
                                    try:
                                        total += f.stat().st_size
                                    except OSError:
                                        pass
                    results.append((label, total))
                self.finished.emit(results)

        class _CleanupView(QWidget):
            def __init__(self) -> None:
                super().__init__()
                layout = QVBoxLayout(self)

                # Description
                desc = QLabel(
                    "Select categories to delete. <b>Recovery packages in reports/cracked/ "
                    "are never touched.</b> Secure deletion is not performed — use a "
                    "dedicated tool if needed."
                )
                desc.setWordWrap(True)
                layout.addWidget(desc)

                # Table
                group = QGroupBox("Workspace Intermediate Files")
                group_layout = QVBoxLayout(group)

                self.table = QTableWidget(len(_CATEGORIES), 3)
                self.table.setHorizontalHeaderLabels(["Category", "Size on Disk", "Notes"])
                self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
                self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
                self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
                self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
                self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                self.table.verticalHeader().setVisible(False)

                for row, (label, _, note) in enumerate(_CATEGORIES):
                    self.table.setItem(row, 0, QTableWidgetItem(label))
                    self.table.setItem(row, 1, QTableWidgetItem("—"))
                    self.table.setItem(row, 2, QTableWidgetItem(note))

                group_layout.addWidget(self.table)
                layout.addWidget(group, 1)

                # Buttons
                btn_row = QHBoxLayout()
                self.btn_refresh = QPushButton("Calculate Sizes")
                self.btn_select_all = QPushButton("Select All")
                self.btn_deselect_all = QPushButton("Deselect All")
                self.btn_clean = QPushButton("Delete Selected Categories")
                self.btn_clean.setStyleSheet("color: red; font-weight: bold;")
                btn_row.addWidget(self.btn_refresh)
                btn_row.addWidget(self.btn_select_all)
                btn_row.addWidget(self.btn_deselect_all)
                btn_row.addStretch()
                btn_row.addWidget(self.btn_clean)
                layout.addLayout(btn_row)

                self.lbl_status = QLabel("")
                layout.addWidget(self.lbl_status)

                # Wire
                self.btn_refresh.clicked.connect(self._calculate_sizes)
                self.btn_select_all.clicked.connect(self.table.selectAll)
                self.btn_deselect_all.clicked.connect(self.table.clearSelection)
                self.btn_clean.clicked.connect(self._clean_selected)

                self._thread: QThread | None = None
                self._worker: _SizeWorker | None = None

            # ------------------------------------------------------------------
            # Helpers
            # ------------------------------------------------------------------

            def _workspace(self):
                from portable_crypt_recovery.app.app_state import get_app_state
                state = get_app_state()
                return state.workspace_root if state.is_workspace_open() else None

            @staticmethod
            def _fmt_size(n: int) -> str:
                if n == 0:
                    return "0 B"
                for unit in ("B", "KB", "MB", "GB"):
                    if n < 1024:
                        return f"{n:.1f} {unit}"
                    n /= 1024
                return f"{n:.1f} TB"

            # ------------------------------------------------------------------
            # Calculate sizes (background thread)
            # ------------------------------------------------------------------

            def _calculate_sizes(self) -> None:
                ws = self._workspace()
                if ws is None:
                    self.lbl_status.setText("No workspace open.")
                    return

                self.btn_refresh.setEnabled(False)
                self.lbl_status.setText("Calculating…")

                # Reset display
                for row in range(len(_CATEGORIES)):
                    self.table.item(row, 1).setText("…")

                self._thread = QThread(self)
                self._worker = _SizeWorker(ws)
                self._worker.moveToThread(self._thread)
                self._thread.started.connect(self._worker.run)
                self._worker.finished.connect(self._on_sizes_ready)
                self._worker.finished.connect(self._thread.quit)
                self._thread.start()

            def _on_sizes_ready(self, results: list) -> None:
                total = 0
                for row, (_, size) in enumerate(results):
                    self.table.item(row, 1).setText(self._fmt_size(size))
                    total += size
                self.lbl_status.setText(
                    f"Total intermediate storage: {self._fmt_size(int(total))}"
                )
                self.btn_refresh.setEnabled(True)

            # ------------------------------------------------------------------
            # Delete selected
            # ------------------------------------------------------------------

            def _clean_selected(self) -> None:
                import shutil
                from pathlib import Path

                ws = self._workspace()
                if ws is None:
                    return

                rows = sorted({idx.row() for idx in self.table.selectedIndexes()})
                if not rows:
                    QMessageBox.information(self, "Nothing Selected", "Select at least one category.")
                    return

                labels = [_CATEGORIES[r][0] for r in rows]
                confirm = QMessageBox.warning(
                    self,
                    "Confirm Deletion",
                    "Permanently delete the following categories?\n\n"
                    + "\n".join(f"  • {l}" for l in labels)
                    + "\n\nThis cannot be undone.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if confirm != QMessageBox.StandardButton.Yes:
                    return

                errors: list[str] = []
                deleted_count = 0
                for row in rows:
                    _, rel_paths, _ = _CATEGORIES[row]
                    for rel in rel_paths:
                        target = ws / rel
                        if not target.exists():
                            continue
                        try:
                            shutil.rmtree(str(target))
                            deleted_count += 1
                        except Exception as exc:
                            errors.append(f"{rel}: {exc}")

                if errors:
                    QMessageBox.warning(
                        self, "Partial Deletion",
                        f"Deleted {deleted_count} folder(s) but {len(errors)} failed:\n"
                        + "\n".join(errors[:5])
                    )
                else:
                    QMessageBox.information(
                        self, "Done",
                        f"Deleted {deleted_count} folder(s).\n"
                        "Run 'Calculate Sizes' to refresh."
                    )

                self.table.clearSelection()
                self._calculate_sizes()

        return _CleanupView()
