"""Report index maintenance."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from portable_crypt_recovery.core.atomic_write import atomic_write_json
from portable_crypt_recovery.models.report import Report

_CSV_PATH = "reports/csv/cracked-results-index.csv"
_JSON_PATH = "reports/json/report-index.json"
_CSV_HEADERS = ["report_id", "job_id", "cracked_timestamp", "report_folder"]


def _csv_path(workspace_root: Path) -> Path:
    return workspace_root / _CSV_PATH


def _json_path(workspace_root: Path) -> Path:
    return workspace_root / _JSON_PATH


def _load_json_index(workspace_root: Path) -> dict[str, Any]:
    path = _json_path(workspace_root)
    if not path.exists():
        return {"schema_version": 1, "reports": []}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def add_report_to_index(workspace_root: Path, report: Report) -> None:
    """Add a completed report to both CSV and JSON indexes."""
    _add_to_json(workspace_root, report)
    _add_to_csv(workspace_root, report)


def _add_to_json(workspace_root: Path, report: Report) -> None:
    index = _load_json_index(workspace_root)
    index["reports"].append(report.to_dict())
    path = _json_path(workspace_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(path, index)


def _add_to_csv(workspace_root: Path, report: Report) -> None:
    csv_file = _csv_path(workspace_root)
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    write_header = not csv_file.exists()
    with csv_file.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_HEADERS)
        if write_header:
            writer.writeheader()
        writer.writerow(
            {
                "report_id": report.report_id,
                "job_id": report.job_id,
                "cracked_timestamp": report.created_timestamp,
                "report_folder": report.report_folder,
            }
        )


def list_reports(workspace_root: Path) -> list[dict[str, Any]]:
    """Return all reports from the JSON index."""
    return _load_json_index(workspace_root).get("reports", [])
