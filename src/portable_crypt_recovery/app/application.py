"""PySide6 application bootstrap."""

from __future__ import annotations

from portable_crypt_recovery import __app_name__
from portable_crypt_recovery.app.startup import ensure_default_portable_layout


def run_app(argv: list[str]) -> int:
    """Start the GUI.

    PySide6 is imported lazily so backend tests can run without creating a GUI.
    """
    from portable_crypt_recovery.app.autosave import start as start_autosave
    from portable_crypt_recovery.app.startup import try_auto_open_workspace, try_detect_hashcat

    app_root = ensure_default_portable_layout()
    opened = try_auto_open_workspace(app_root)
    try_detect_hashcat(app_root)

    try:
        from PySide6.QtWidgets import QApplication
    except ImportError as exc:  # pragma: no cover - depends on local dev environment
        print("PySide6 is required to run the GUI. Install with: python -m pip install -e .")
        raise SystemExit(2) from exc

    from portable_crypt_recovery.ui.disclaimer_dialog import DisclaimerDialog
    from portable_crypt_recovery.ui.main_window import MainWindow

    app = QApplication(argv)
    app.setApplicationName(__app_name__)

    # Show disclaimer on every launch — must be accepted to continue
    dlg = DisclaimerDialog()
    if dlg.exec() != dlg.Accepted:
        return 0

    window = MainWindow()
    window.show()

    # Start periodic settings autosave (every 60 s)
    start_autosave()

    # Check for a stale runner lock from a previous crash
    if opened:
        from PySide6.QtCore import QTimer

        from portable_crypt_recovery.app.app_state import get_app_state
        ws_root = get_app_state().workspace_root
        if ws_root is not None:
            QTimer.singleShot(500, lambda: _check_stale_lock(ws_root))

    return app.exec()


def _check_stale_lock(workspace_root) -> None:  # pragma: no cover
    """Prompt the user to remove a stale runner lock if one is found."""
    import json
    import os
    from pathlib import Path

    lock_file = Path(workspace_root) / "queue" / "runner-lock.json"
    if not lock_file.exists():
        return

    try:
        with lock_file.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        pid = int(data.get("pid", 0))
        if pid:
            try:
                os.kill(pid, 0)
                return  # process is alive — lock is valid
            except ProcessLookupError:
                pass  # process gone — stale lock
            except PermissionError:
                return  # alive but owned by another user
            except OSError:
                return  # be conservative
    except Exception:
        pass

    # Stale lock found — ask user
    from PySide6.QtWidgets import QMessageBox
    msg = QMessageBox()
    msg.setWindowTitle("Stale Queue Lock Detected")
    msg.setText(
        "A queue lock file was found, but the previous process is no longer running.\n\n"
        "This usually means the app was closed while the queue was active.\n\n"
        "Remove the stale lock so the queue can be started again?"
    )
    msg.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    msg.setDefaultButton(QMessageBox.StandardButton.Yes)
    if msg.exec() == QMessageBox.StandardButton.Yes:
        lock_file.unlink(missing_ok=True)
