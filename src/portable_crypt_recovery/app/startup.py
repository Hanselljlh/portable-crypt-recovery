"""Startup helpers for the portable folder layout."""

from __future__ import annotations

import json
from pathlib import Path

from portable_crypt_recovery.core.paths import app_root_from_cwd

PORTABLE_DIRS = (
    "app",
    "tools/hashcat",
    "workspaces/default",
    "config",
    "logs",
    "docs",
)


def ensure_default_portable_layout(root: Path | None = None) -> Path:
    """Create the default PCR portable folders when they are missing.

    The function only creates folders. It does not create or move sensitive recovery data.
    """
    base = root or app_root_from_cwd()
    for folder in PORTABLE_DIRS:
        (base / folder).mkdir(parents=True, exist_ok=True)
    return base


def try_auto_open_workspace(app_root: Path) -> bool:
    """Open the default workspace into AppState if it exists.

    Returns True if a workspace was successfully opened.
    """
    from portable_crypt_recovery.app.app_state import get_app_state
    from portable_crypt_recovery.workspace.workspace_manager import create_or_open_workspace

    default_ws_root = app_root / "workspaces" / "default"

    # Only auto-open if workspace.json already exists (don't create one silently)
    if not (default_ws_root / "workspace.json").exists():
        return False

    try:
        ws = create_or_open_workspace(default_ws_root)
    except Exception:
        return False

    state = get_app_state()
    state.load_from_workspace(ws.root, ws.record)

    # Load settings
    settings_file = ws.root / "settings.json"
    if settings_file.exists():
        try:
            settings = json.loads(settings_file.read_text(encoding="utf-8"))
            state.load_settings(settings)
            hc_path = settings.get("hashcat_path")
            if hc_path and Path(hc_path).exists():
                state.hashcat_setup.executable_path = hc_path
                state.hashcat_setup.verified = bool(settings.get("hashcat_verified", False))
                state.hashcat_setup.version_string = settings.get("hashcat_version", "")
                device_ids = settings.get("selected_compute_devices", [])
                if device_ids:
                    state.hashcat_setup.selected_compute_devices = [int(d) for d in device_ids]
        except Exception:
            pass

    # Count targets
    try:
        targets_file = ws.root / "targets" / "targets.json"
        if targets_file.exists():
            data = json.loads(targets_file.read_text(encoding="utf-8"))
            state.target_count = len(data.get("targets", []))
    except Exception:
        pass

    # Count headers
    try:
        metadata_dir = ws.root / "headers" / "metadata"
        if metadata_dir.exists():
            state.header_count = sum(
                1 for p in metadata_dir.iterdir()
                if p.suffix == ".json" and p.stem.startswith("header_")
            )
    except Exception:
        pass

    # Count queue jobs
    try:
        queue_file = ws.root / "queue" / "queue-state.json"
        if queue_file.exists():
            qs_data = json.loads(queue_file.read_text(encoding="utf-8"))
            state.job_count = len(qs_data.get("jobs", {}))
    except Exception:
        pass

    return True
