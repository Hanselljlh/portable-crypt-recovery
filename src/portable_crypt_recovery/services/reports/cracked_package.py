"""Assemble per-cracked-job recovery packages."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from portable_crypt_recovery.core.atomic_write import atomic_write_json
from portable_crypt_recovery.core.timestamps import utc_now_iso
from portable_crypt_recovery.models.report import Report
from portable_crypt_recovery.models.task import QueuedTask


def assemble_cracked_package(
    workspace_root: Path,
    job: QueuedTask,
    report: Report,
    cracked_password: str,
    run_id: str,
) -> Path:
    """Copy header, keyfiles, and write manifest into the recovery package folder.

    Returns the package folder path.
    """
    pkg_dir = workspace_root / "reports" / "cracked" / f"task_{job.task_id}_run_{run_id}"
    pkg_dir.mkdir(parents=True, exist_ok=True)

    # Copy normalized header
    header_src = workspace_root / report.recovered_header_path
    if header_src.exists():
        shutil.copy2(header_src, pkg_dir / "normalized-header.bin")

    # Copy keyfiles if used
    kf_manifest: list[dict] = []
    if job.keyfile_set_id:
        kf_set_path = (
            workspace_root / "generated" / "keyfile-lists" / f"{job.keyfile_set_id}.json"
        )
        if kf_set_path.exists():
            with kf_set_path.open("r", encoding="utf-8") as fh:
                kf_data = json.load(fh)
            from portable_crypt_recovery.models.keyfile_set import KeyfileSet
            kf_set = KeyfileSet.from_dict(kf_data)
            for entry in kf_set.entries:
                kf_src = workspace_root / entry.normalized_workspace_path
                if kf_src.exists():
                    dest = pkg_dir / f"keyfile_{entry.keyfile_id}{kf_src.suffix}"
                    shutil.copy2(kf_src, dest)
                    kf_manifest.append(
                        {
                            "keyfile_id": entry.keyfile_id,
                            "original_path": entry.original_path,
                            "package_filename": dest.name,
                        }
                    )

    # Write package manifest
    manifest_data = {
        "schema_version": 1,
        "created_timestamp": utc_now_iso(),
        "job_id": job.task_id,
        "report_id": report.report_id,
        "hashcat_mode": job.hashcat_mode,
        "pim_mode": job.pim_mode,
        "pim_value": job.pim_value,
        "keyfiles": kf_manifest,
        "notes": "This folder contains sensitive recovery data. Keep it secure.",
    }
    atomic_write_json(pkg_dir / "recovery-package-manifest.json", manifest_data)

    return pkg_dir
