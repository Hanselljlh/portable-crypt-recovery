"""Logs view — tabbed log viewer."""

from __future__ import annotations

from pathlib import Path

_LOG_MAX_BYTES = 200 * 1024  # 200 KB tail — prevents startup freeze on large logs


def read_log_tail(path: Path, max_bytes: int = _LOG_MAX_BYTES) -> str:
    """Return the tail of *path* as a UTF-8 string, capped at *max_bytes*.

    When the file is larger than *max_bytes*, the returned string starts with a
    single-line truncation notice so the user knows content was omitted.
    Encoding errors are replaced rather than raised.
    """
    if not path.exists():
        return f"Log file not found: {path}"
    try:
        size = path.stat().st_size
        if size <= max_bytes:
            return path.read_text(encoding="utf-8", errors="replace")
        with path.open("rb") as fh:
            fh.seek(-max_bytes, 2)
            raw = fh.read()
        # Drop any partial line at the cut point
        first_nl = raw.find(b"\n")
        if first_nl >= 0:
            raw = raw[first_nl + 1:]
        tail = raw.decode("utf-8", errors="replace")
        kb = max_bytes // 1024
        return f"[... log truncated — showing last {kb} KB of {size // 1024} KB ...]\n\n{tail}"
    except OSError as exc:
        return f"Could not read: {path}\n{exc}"


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
                from portable_crypt_recovery.app.app_state import get_app_state
                ws = get_app_state().workspace_root
                if ws is None:
                    for w in (self.txt_app, self.txt_queue, self.txt_error):
                        w.setPlainText("No workspace open.")
                    return
                self._load_log(self.txt_app, ws / "logs" / "app" / "app.log")
                self._load_log(self.txt_queue, ws / "logs" / "queue" / "queue.log")
                self._load_log(self.txt_error, ws / "logs" / "errors" / "error.log")

            @staticmethod
            def _load_log(widget, path) -> None:
                widget.setPlainText(read_log_tail(path))

        return _LogsView(workspace_root)
