"""Workspace summary generator (no sensitive data)."""

from __future__ import annotations

import json
from pathlib import Path


def generate_workspace_summary(workspace_root: Path) -> str:
    """Return a text summary of workspace statistics with no sensitive data."""
    lines = ["Workspace Summary", "=================", f"Root: {workspace_root}", ""]

    # Workspace record
    ws_file = workspace_root / "workspace.json"
    if ws_file.exists():
        with ws_file.open("r", encoding="utf-8") as fh:
            ws = json.load(fh)
        lines.append(f"Workspace ID:   {ws.get('workspace_id', 'unknown')}")
        lines.append(f"Workspace Name: {ws.get('workspace_name', 'unknown')}")
        lines.append(f"Created:        {ws.get('created_timestamp', 'unknown')}")
        lines.append(f"App Version:    {ws.get('app_version', 'unknown')}")
        lines.append("")

    # Targets
    target_file = workspace_root / "targets" / "targets.json"
    target_count = 0
    if target_file.exists():
        with target_file.open("r", encoding="utf-8") as fh:
            td = json.load(fh)
        target_count = len(td.get("targets", []))
    lines.append(f"Targets: {target_count}")

    # Headers
    header_dir = workspace_root / "headers" / "metadata"
    header_count = len(list(header_dir.glob("*.json"))) if header_dir.exists() else 0
    lines.append(f"Headers: {header_count}")

    # Tasks (support legacy files that still use the old "jobs" key)
    queue_file = workspace_root / "queue" / "queue-state.json"
    task_count = 0
    if queue_file.exists():
        with queue_file.open("r", encoding="utf-8") as fh:
            qd = json.load(fh)
        tasks_map = qd["tasks"] if "tasks" in qd else qd.get("jobs", {})
        task_count = len(tasks_map)
    lines.append(f"Tasks:   {task_count}")

    # Reports
    reports_dir = workspace_root / "reports" / "cracked"
    report_count = len(list(reports_dir.iterdir())) if reports_dir.exists() else 0
    lines.append(f"Reports: {report_count}")

    return "\n".join(lines) + "\n"
