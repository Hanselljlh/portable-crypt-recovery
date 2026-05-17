"""Workspace schema defaults."""

from __future__ import annotations

from portable_crypt_recovery import __version__
from portable_crypt_recovery.core.ids import new_id
from portable_crypt_recovery.core.platform_info import platform_summary
from portable_crypt_recovery.core.timestamps import utc_now_iso

WORKSPACE_SCHEMA_VERSION = 1


def new_workspace_record(name: str) -> dict:
    now = utc_now_iso()
    return {
        "schema_version": WORKSPACE_SCHEMA_VERSION,
        "workspace_id": new_id("workspace"),
        "workspace_name": name,
        "created_timestamp": now,
        "last_opened_timestamp": now,
        "app_version": __version__,
        "created_platform": platform_summary(),
        "notes": "",
    }


def default_settings_record() -> dict:
    return {
        "schema_version": WORKSPACE_SCHEMA_VERSION,
        "hashcat_path": None,
        "hashcat_path_is_external": False,
        "selected_compute_devices": [],
        "default_queue_behavior_after_crack": "continue_other_uncracked_targets",
        "clipboard_auto_clear_seconds": 60,
        "safety_confirmation_status": False,
    }


def empty_targets_record() -> dict:
    return {"schema_version": WORKSPACE_SCHEMA_VERSION, "targets": []}


def empty_queue_state_record() -> dict:
    return {
        "schema_version": WORKSPACE_SCHEMA_VERSION,
        "queue_order": [],
        "current_running_job": None,
        "status": "stopped",
        "jobs": {},
    }


def empty_cleanup_manifest_record() -> dict:
    return {"schema_version": WORKSPACE_SCHEMA_VERSION, "entries": []}
