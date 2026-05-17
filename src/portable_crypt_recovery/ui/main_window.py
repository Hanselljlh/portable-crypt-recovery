"""Main application window."""

from __future__ import annotations

from portable_crypt_recovery import __app_name__, __version__

SCREEN_NAMES = (
    "Dashboard",
    "Targets",
    "Jobs",
    "Queue",
    "Logs",
    "Reports",
    "Settings",
)


class MainWindow:  # pragma: no cover - covered by manual GUI tests
    """Main GUI window.

    The class is defined with runtime PySide6 imports so the package can be imported in
    non-GUI test environments.
    """

    def __new__(cls):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QHBoxLayout,
            QLabel,
            QListWidget,
            QListWidgetItem,
            QMainWindow,
            QStackedWidget,
            QVBoxLayout,
            QWidget,
        )

        class _MainWindow(QMainWindow):
            def __init__(self) -> None:
                super().__init__()
                self.setWindowTitle(f"{__app_name__} {__version__}")
                self.resize(1100, 720)

                root = QWidget()
                layout = QHBoxLayout(root)

                self.nav = QListWidget()
                self.nav.setMaximumWidth(220)
                self.stack = QStackedWidget()

                for name in SCREEN_NAMES:
                    self.nav.addItem(QListWidgetItem(name))
                    page = QWidget()
                    page_layout = QVBoxLayout(page)
                    title = QLabel(name)
                    title.setAlignment(Qt.AlignLeft)
                    title.setStyleSheet("font-size: 22px; font-weight: 600;")
                    body = QLabel(self._placeholder_text(name))
                    body.setWordWrap(True)
                    body.setAlignment(Qt.AlignTop | Qt.AlignLeft)
                    page_layout.addWidget(title)
                    page_layout.addWidget(body)
                    page_layout.addStretch()
                    self.stack.addWidget(page)

                self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
                self.nav.setCurrentRow(0)

                layout.addWidget(self.nav)
                layout.addWidget(self.stack, 1)
                self.setCentralWidget(root)

            @staticmethod
            def _placeholder_text(name: str) -> str:
                if name == "Dashboard":
                    return (
                        "Workspace status, Hashcat setup status, target count, queued jobs, "
                        "and recent activity will appear here."
                    )
                if name == "Targets":
                    return (
                        "Add VeraCrypt or TrueCrypt file containers, disk images, or already "
                        "extracted headers. Raw physical device access is Future."
                    )
                if name == "Jobs":
                    return "Build mode, PIM, keyfile, and password source job drafts here."
                if name == "Queue":
                    return "Run one Hashcat job at a time, pause, stop, resume, skip, and restart jobs."
                if name == "Logs":
                    return "App, queue, Hashcat, and error logs will be shown here."
                if name == "Reports":
                    return "Cracked-result reports and recovery folders will be shown here."
                if name == "Settings":
                    return "Configure workspace, Hashcat path, devices, and app preferences here."
                return ""

        return _MainWindow()
