"""Logs view — tabbed log viewer."""

from __future__ import annotations


class LogsView:  # pragma: no cover
    """Tabbed viewer for app log, queue log, and error log."""

    def __new__(cls, workspace_root=None):
        from PySide6.QtWidgets import (
            QHBoxLayout,
            QPlainTextEdit,
            QPushButton,
            QTabWidget,
            QVBoxLayout,
            QWidget,
        )

        class _LogsView(QWidget):
            def __init__(self, workspace_root=None) -> None:
                super().__init__()
                self.workspace_root = workspace_root
                layout = QVBoxLayout(self)

                toolbar = QHBoxLayout()
                self.btn_refresh = QPushButton("Refresh")
                self.btn_refresh.clicked.connect(self.refresh)
                toolbar.addWidget(self.btn_refresh)
                toolbar.addStretch()
                layout.addLayout(toolbar)

                self.tabs = QTabWidget()
                self.txt_app = QPlainTextEdit()
                self.txt_app.setReadOnly(True)
                self.txt_queue = QPlainTextEdit()
                self.txt_queue.setReadOnly(True)
                self.txt_error = QPlainTextEdit()
                self.txt_error.setReadOnly(True)

                self.tabs.addTab(self.txt_app, "App Log")
                self.tabs.addTab(self.txt_queue, "Queue Log")
                self.tabs.addTab(self.txt_error, "Error Log")
                layout.addWidget(self.tabs, 1)

                self.refresh()

            def refresh(self) -> None:
                if self.workspace_root is None:
                    return
                self._load_log(self.txt_app, self.workspace_root / "logs" / "app" / "app.log")
                self._load_log(self.txt_queue, self.workspace_root / "logs" / "queue" / "queue.log")
                self._load_log(self.txt_error, self.workspace_root / "logs" / "errors" / "error.log")

            @staticmethod
            def _load_log(widget, path) -> None:
                if path.exists():
                    try:
                        widget.setPlainText(path.read_text(encoding="utf-8", errors="replace"))
                    except OSError:
                        widget.setPlainText(f"Could not read: {path}")
                else:
                    widget.setPlainText(f"Log file not found: {path}")

        return _LogsView(workspace_root)
