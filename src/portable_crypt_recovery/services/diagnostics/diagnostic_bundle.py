"""Diagnostic bundle export."""

from __future__ import annotations

import platform
import zipfile
from pathlib import Path

from portable_crypt_recovery import __version__
from portable_crypt_recovery.core.ids import new_id
from portable_crypt_recovery.core.timestamps import utc_now_iso
from portable_crypt_recovery.models.diagnostic_bundle import DiagnosticBundle
from portable_crypt_recovery.services.diagnostics.log_sanitizer import sanitize_log_file
from portable_crypt_recovery.services.diagnostics.workspace_summary import (
    generate_workspace_summary,
)

# Categories always excluded from bundles
_EXCLUDED_CATEGORIES = [
    "passwords",
    "headers",
    "keyfiles",
    "potfiles",
    "wordlists",
    "cracked_results",
]


def export_diagnostic_bundle(
    workspace_root: Path,
    hashcat_version: str | None = None,
) -> DiagnosticBundle:
    """Export a sanitized diagnostic zip to reports/diagnostics/.

    Includes: sanitized logs, workspace summary, app version, OS, schema version,
    Hashcat version.
    Excludes: passwords, headers, keyfiles, potfiles, wordlists, cracked results.

    Returns the DiagnosticBundle metadata object.
    """
    bundle_id = new_id("bundle")
    now_ts = utc_now_iso()
    out_dir = workspace_root / "reports" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"diagnostic_bundle_{now_ts.replace(':', '-')}.zip"

    ws_summary = generate_workspace_summary(workspace_root)
    os_summary = f"{platform.system()} {platform.release()} {platform.version()}"

    included_files: list[str] = []

    # Workspace info
    workspace_json = workspace_root / "workspace.json"
    workspace_id = ""
    if workspace_json.exists():
        try:
            import json as _json
            workspace_id = _json.loads(
                workspace_json.read_text(encoding="utf-8")
            ).get("workspace_id", "")
        except Exception:
            pass

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Workspace summary (no sensitive data)
        zf.writestr("workspace-summary.txt", ws_summary)
        included_files.append("workspace-summary.txt")

        # App/OS meta
        meta = (
            f"App Version: {__version__}\n"
            f"OS: {os_summary}\n"
            f"Hashcat Version: {hashcat_version or 'unknown'}\n"
            f"Schema Version: 1\n"
            f"Bundle Created: {now_ts}\n"
        )
        zf.writestr("bundle-meta.txt", meta)
        included_files.append("bundle-meta.txt")

        # Sanitized app log
        for log_glob_path in (workspace_root / "logs").rglob("*.log"):
            sanitized = sanitize_log_file(log_glob_path)
            arc_name = f"logs/{log_glob_path.name}.sanitized.txt"
            zf.writestr(arc_name, "\n".join(sanitized))
            included_files.append(arc_name)

        # workspace.json (no sensitive data by design)
        if workspace_json.exists():
            zf.write(workspace_json, "workspace.json")
            included_files.append("workspace.json")

    bundle = DiagnosticBundle(
        bundle_id=bundle_id,
        created_timestamp=now_ts,
        workspace_id=workspace_id,
        app_version=__version__,
        os_summary=os_summary,
        hashcat_version=hashcat_version,
        schema_version=1,
        included_files=included_files,
        excluded_categories=_EXCLUDED_CATEGORIES,
        bundle_path=str(zip_path.relative_to(workspace_root).as_posix()),
    )

    return bundle
