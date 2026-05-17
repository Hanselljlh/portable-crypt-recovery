"""PySide6 application bootstrap."""

from __future__ import annotations

from portable_crypt_recovery import __app_name__
from portable_crypt_recovery.app.startup import ensure_default_portable_layout


def run_app(argv: list[str]) -> int:
    """Start the GUI.

    PySide6 is imported lazily so backend tests can run without creating a GUI.
    """
    from portable_crypt_recovery.app.startup import try_auto_open_workspace

    app_root = ensure_default_portable_layout()
    try_auto_open_workspace(app_root)

    try:
        from PySide6.QtWidgets import QApplication
    except ImportError as exc:  # pragma: no cover - depends on local dev environment
        print("PySide6 is required to run the GUI. Install with: python -m pip install -e .")
        raise SystemExit(2) from exc

    from portable_crypt_recovery.ui.main_window import MainWindow

    app = QApplication(argv)
    app.setApplicationName(__app_name__)
    window = MainWindow()
    window.show()
    return app.exec()
