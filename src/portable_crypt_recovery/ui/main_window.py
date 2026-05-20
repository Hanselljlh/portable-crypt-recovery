"""Main application window."""

from __future__ import annotations

from portable_crypt_recovery import __app_name__, __version__

SCREEN_NAMES = (
    "Setup",
    "Targets",
    "Passwords",
    "Jobs",
    "Queue",
    "Reports",
    "Cleanup",
    "Settings",
)


class MainWindow:  # pragma: no cover - covered by manual GUI tests
    """Main GUI window.

    The class is defined with runtime PySide6 imports so the package can be imported in
    non-GUI test environments.
    """

    def __new__(cls):
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QAction, QDesktopServices
        from PySide6.QtWidgets import (
            QListWidget,
            QListWidgetItem,
            QMainWindow,
            QSplitter,
            QStackedWidget,
            QWidget,
        )

        from portable_crypt_recovery.ui.cleanup_view import CleanupView
        from portable_crypt_recovery.ui.jobs_view import JobsView
        from portable_crypt_recovery.ui.password_builder_view import PasswordBuilderView
        from portable_crypt_recovery.ui.queue_view import QueueView
        from portable_crypt_recovery.ui.reports_view import ReportsView
        from portable_crypt_recovery.ui.settings_view import SettingsView
        from portable_crypt_recovery.ui.setup_view import SetupView
        from portable_crypt_recovery.ui.targets_view import TargetsView

        class _MainWindow(QMainWindow):
            def __init__(self) -> None:
                super().__init__()
                self.setWindowTitle(f"{__app_name__} {__version__}")
                self.resize(1150, 740)

                # Resizable nav/content split
                from PySide6.QtCore import Qt  # noqa: PLC0415
                self._splitter = QSplitter(Qt.Orientation.Horizontal)

                self.nav = QListWidget()
                self.nav.setMinimumWidth(140)
                self.stack = QStackedWidget()

                # Build views in SCREEN_NAMES order
                views = [
                    SetupView(),
                    TargetsView(),
                    PasswordBuilderView(),
                    JobsView(),
                    QueueView(),
                    ReportsView(),
                    CleanupView(),
                    SettingsView(),
                ]

                for name, view in zip(SCREEN_NAMES, views, strict=False):
                    self.nav.addItem(QListWidgetItem(name))
                    self.stack.addWidget(view)

                self.nav.currentRowChanged.connect(self._on_nav_changed)
                self.nav.setCurrentRow(0)

                self._splitter.addWidget(self.nav)
                self._splitter.addWidget(self.stack)
                # Default split: 200 px nav, rest to content
                self._splitter.setSizes([200, 950])
                self._splitter.setStretchFactor(0, 0)
                self._splitter.setStretchFactor(1, 1)

                root = QWidget()
                from PySide6.QtWidgets import QHBoxLayout  # noqa: PLC0415
                layout = QHBoxLayout(root)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(self._splitter)
                self.setCentralWidget(root)

                # Help menu
                self._build_help_menu()

                # Navigate to Settings on first launch if no workspace loaded
                from PySide6.QtCore import QTimer
                QTimer.singleShot(150, self._check_first_run)

            def _on_nav_changed(self, index: int) -> None:
                """Switch stack page and refresh the view if it supports it."""
                self.stack.setCurrentIndex(index)
                view = self.stack.widget(index)
                if hasattr(view, "_refresh_list"):
                    view._refresh_list()

            def _check_first_run(self) -> None:
                from PySide6.QtWidgets import QMessageBox  # noqa: PLC0415

                from portable_crypt_recovery.app.app_state import get_app_state
                if not get_app_state().is_workspace_open():
                    # Stay on the Setup screen — it already shows status at a
                    # glance and has buttons that deep-link to Settings.
                    QMessageBox.information(
                        self,
                        "Welcome — Setup Required",
                        "No workspace is loaded.\n\n"
                        "To get started:\n"
                        "  1. Click 'Open / Change Workspace…' on this screen\n"
                        "     and select the workspaces\\default\\ folder.\n\n"
                        "  2. Click 'Configure Hashcat…' and browse to hashcat.exe,\n"
                        "     then click Verify (or use 'Use Portable Tools Folder'\n"
                        "     if hashcat is already in tools\\hashcat\\).\n\n"
                        "This Setup screen shows status at a glance once configured.",
                    )

            def _build_help_menu(self) -> None:
                menubar = self.menuBar()
                help_menu = menubar.addMenu("Help")

                action_user_guide = QAction("Open User Guide", self)
                action_user_guide.triggered.connect(self._open_user_guide)
                help_menu.addAction(action_user_guide)

                action_open_ws = QAction("Open Workspace Folder", self)
                action_open_ws.triggered.connect(self._open_workspace_folder)
                help_menu.addAction(action_open_ws)

                action_open_logs = QAction("Open Logs Folder", self)
                action_open_logs.triggered.connect(self._open_logs_folder)
                help_menu.addAction(action_open_logs)

                action_diagnostic = QAction("Export Diagnostic Bundle", self)
                action_diagnostic.triggered.connect(self._export_diagnostic)
                help_menu.addAction(action_diagnostic)

                action_github = QAction("Report Issue on GitHub", self)
                action_github.triggered.connect(self._open_github_issues)
                help_menu.addAction(action_github)

            def _open_user_guide(self) -> None:
                import os
                import subprocess
                import sys

                from portable_crypt_recovery.core.paths import app_root_from_cwd
                docs_path = app_root_from_cwd() / "docs" / "user-guide" / "getting-started.md"
                if docs_path.exists():
                    if sys.platform == "win32":
                        os.startfile(str(docs_path))
                    else:
                        subprocess.Popen(["xdg-open", str(docs_path)])

            def _open_workspace_folder(self) -> None:
                import os
                import subprocess
                import sys

                from portable_crypt_recovery.app.app_state import get_app_state
                state = get_app_state()
                if state.workspace_root and state.workspace_root.exists():
                    if sys.platform == "win32":
                        os.startfile(str(state.workspace_root))
                    else:
                        subprocess.Popen(["xdg-open", str(state.workspace_root)])

            def _open_logs_folder(self) -> None:
                import os
                import subprocess
                import sys

                from portable_crypt_recovery.app.app_state import get_app_state
                state = get_app_state()
                if state.workspace_root:
                    logs_dir = state.workspace_root / "logs"
                    if logs_dir.exists():
                        if sys.platform == "win32":
                            os.startfile(str(logs_dir))
                        else:
                            subprocess.Popen(["xdg-open", str(logs_dir)])

            def _export_diagnostic(self) -> None:
                import os
                import subprocess
                import sys

                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                state = get_app_state()
                if not state.workspace_root:
                    QMessageBox.warning(self, "No Workspace", "Open a workspace first.")
                    return
                from portable_crypt_recovery.services.diagnostics.diagnostic_bundle import (
                    export_diagnostic_bundle,
                )
                bundle = export_diagnostic_bundle(
                    state.workspace_root,
                    state.hashcat_setup.version_string or None,
                )
                abs_path = state.workspace_root / bundle.bundle_path
                reply = QMessageBox.information(
                    self,
                    "Diagnostic Bundle Exported",
                    f"Saved to:\n{abs_path}\n\nOpen the containing folder?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    folder = abs_path.parent
                    if folder.exists():
                        if sys.platform == "win32":
                            os.startfile(str(folder))
                        else:
                            subprocess.Popen(["xdg-open", str(folder)])

            def _open_github_issues(self) -> None:
                QDesktopServices.openUrl(
                    QUrl("https://github.com/Hanselljlh/portable-crypt-recovery/issues")
                )

        return _MainWindow()
