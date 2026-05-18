"""Report generator for cracked jobs."""

from __future__ import annotations

from pathlib import Path

from portable_crypt_recovery.core.atomic_write import atomic_write_json, atomic_write_text
from portable_crypt_recovery.core.ids import new_id
from portable_crypt_recovery.core.timestamps import utc_now_iso
from portable_crypt_recovery.models.report import Report
from portable_crypt_recovery.models.task import QueuedTask
from portable_crypt_recovery.services.reports.cracked_package import assemble_cracked_package
from portable_crypt_recovery.services.reports.report_index import add_report_to_index

_HOW_TO_OPEN = """\
How to Open This Volume
=======================

WARNING: Keep this folder secure. It contains sensitive recovery data.

1. The recovered password is documented in recovered-result.txt.
   Do NOT share this file.

2. If keyfiles are in this package, they must be present when mounting.

3. To open a VeraCrypt volume:
   - Use VeraCrypt (veracrypt.io) or TrueCrypt 7.1a
   - Select the volume file
   - Enter the recovered password
   - Select any required keyfiles

4. VeraCrypt 1.26+ removed support for TrueCrypt volumes and legacy
   RIPEMD-160 / GOST89 mounting. Use VeraCrypt 1.25.9 for those.

5. If mounting fails, confirm the correct header candidate was used.

Portable Crypt Recovery cannot guarantee which version of VeraCrypt
or TrueCrypt is required. These are guidance notes only.
"""


def generate_cracked_report(
    workspace_root: Path,
    job: QueuedTask,
    cracked_password: str,
    stats_text: str = "",
    run_id: str | None = None,
) -> Report:
    """Generate full report files for a cracked job.

    Creates reports/cracked/job_<id>_run_<id>/ with all report files.
    Adds to the report index.
    Returns the Report model.

    NOTE: The caller must have already saved the raw cracked password
    before calling this function.
    """
    run_id = run_id or new_id("run")
    report_id = new_id("report")
    now = utc_now_iso()

    # Resolve header path
    recovered_header_path = ""
    try:
        from portable_crypt_recovery.services.headers.metadata import load_header_metadata
        header_meta = load_header_metadata(workspace_root, job.header_id)
        recovered_header_path = header_meta.workspace_relative_path
    except Exception:
        pass

    report = Report(
        report_id=report_id,
        job_id=job.task_id,
        cracked_password=cracked_password,
        recovered_header_path=recovered_header_path,
        command_used=job.command_array,
        stats_text=stats_text,
        created_timestamp=now,
    )

    # Build package folder
    pkg_dir = assemble_cracked_package(
        workspace_root=workspace_root,
        job=job,
        report=report,
        cracked_password=cracked_password,
        run_id=run_id,
    )

    report.report_folder = str(
        pkg_dir.relative_to(workspace_root).as_posix()
    )

    # Write recovered-result.txt  (NEVER log passwords in app log)
    atomic_write_text(
        pkg_dir / "recovered-result.txt",
        f"Recovered Password: {cracked_password}\n"
        f"Task ID: {job.task_id}\n"
        f"Hashcat Mode: {job.hashcat_mode}\n"
        f"PIM Mode: {job.pim_mode}\n"
        f"PIM Value: {job.pim_value}\n"
        f"Recovered Timestamp: {now}\n",
    )

    # Write recovered-result.json
    atomic_write_json(
        pkg_dir / "recovered-result.json",
        {
            "schema_version": 1,
            "report_id": report_id,
            "job_id": job.task_id,
            "cracked_password": cracked_password,
            "hashcat_mode": job.hashcat_mode,
            "pim_mode": job.pim_mode,
            "pim_value": job.pim_value,
            "created_timestamp": now,
        },
    )

    # Write recovered-result.md
    atomic_write_text(
        pkg_dir / "recovered-result.md",
        f"# Recovery Report\n\n"
        f"**Task ID:** `{job.task_id}`\n\n"
        f"**Recovered:** {now}\n\n"
        f"**Hashcat Mode:** {job.hashcat_mode}\n\n"
        f"**PIM:** {job.pim_mode} ({job.pim_value})\n\n"
        f"**Password:** See `recovered-result.txt`\n",
    )

    # Write stats.txt
    if stats_text:
        atomic_write_text(pkg_dir / "stats.txt", stats_text)

    # Write command-used.txt
    atomic_write_text(
        pkg_dir / "command-used.txt",
        "Command used (argument array — never a shell string):\n\n"
        + "\n".join(f"  {arg}" for arg in job.command_array) + "\n",
    )

    # Write how-to-open-this-volume.txt
    atomic_write_text(pkg_dir / "how-to-open-this-volume.txt", _HOW_TO_OPEN)

    # Add to index
    add_report_to_index(workspace_root, report)

    return report
