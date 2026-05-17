"""Final job expander: HashModeSet x PimSet x KeyfileSet x PasswordSource -> list[QueuedJob]."""

from __future__ import annotations

from pathlib import Path

from portable_crypt_recovery.core.ids import new_id
from portable_crypt_recovery.core.paths import to_workspace_relative
from portable_crypt_recovery.core.timestamps import utc_now_iso
from portable_crypt_recovery.models.hash_mode_set import HashModeSet
from portable_crypt_recovery.models.job import QueuedJob
from portable_crypt_recovery.models.keyfile_set import KeyfileSet
from portable_crypt_recovery.models.password_source import PasswordSource
from portable_crypt_recovery.models.pim_set import PimSet


def expand_jobs(
    target_id: str,
    header_id: str,
    mode_set: HashModeSet,
    pim_set: PimSet,
    keyfile_sets: list[KeyfileSet] | None,
    password_source: PasswordSource,
    workspace_root: Path,
) -> list[QueuedJob]:
    """Expand all combinations into a list of QueuedJob objects.

    Each job gets a unique session name and workspace-local paths.

    Parameters
    ----------
    target_id:
        Target ID.
    header_id:
        Header ID.
    mode_set:
        HashModeSet containing one or more mode entries.
    pim_set:
        PimSet (default or custom with values).
    keyfile_sets:
        List of KeyfileSet combinations (or None/empty for no keyfiles).
    password_source:
        Password source (wordlist or generated).
    workspace_root:
        Workspace root for constructing paths.
    """
    jobs: list[QueuedJob] = []
    now = utc_now_iso()

    # Resolve PIM iterations
    pim_iterations: list[tuple[str, int | None]] = []  # (pim_mode, pim_value)
    if pim_set.pim_mode == "default":
        pim_iterations = [("default", None)]
    else:
        pim_iterations = [("custom", v) for v in pim_set.values]

    # Resolve keyfile set iterations
    kf_iterations: list[KeyfileSet | None]
    if not keyfile_sets:
        kf_iterations = [None]
    else:
        kf_iterations = list(keyfile_sets)  # type: ignore[assignment]

    for mode_entry in mode_set.entries:
        for pim_mode, pim_value in pim_iterations:
            for kf_set in kf_iterations:
                job_id = new_id("job")
                session_name = f"pcr_{job_id}"

                # Paths (workspace-relative)
                potfile_rel = f"hashcat/potfile/{session_name}.potfile"
                outfile_rel = f"hashcat/output/{session_name}.out"
                log_rel = f"hashcat/logs/{session_name}.log"

                # Validate paths are inside workspace
                _validate_workspace_path(workspace_root, potfile_rel)
                _validate_workspace_path(workspace_root, outfile_rel)
                _validate_workspace_path(workspace_root, log_rel)

                kf_set_id = kf_set.set_id if kf_set is not None else None

                job = QueuedJob(
                    job_id=job_id,
                    target_id=target_id,
                    header_id=header_id,
                    hash_mode_set_id=mode_set.mode_set_id,
                    pim_set_id=pim_set.pim_set_id,
                    keyfile_set_id=kf_set_id,
                    password_source_id=password_source.source_id,
                    status="pending",
                    command_array=[],  # built by command_builder at run time
                    potfile_path=potfile_rel,
                    outfile_path=outfile_rel,
                    log_path=log_rel,
                    session_name=session_name,
                    hashcat_mode=mode_entry.mode,
                    pim_value=pim_value,
                    pim_mode=pim_mode,
                    wordlist_path=password_source.workspace_relative_path or "",
                    created_timestamp=now,
                    updated_timestamp=now,
                )
                jobs.append(job)

    return jobs


def _validate_workspace_path(workspace_root: Path, relative_path: str) -> None:
    """Ensure a relative path stays inside the workspace."""
    from portable_crypt_recovery.core.paths import safe_join_workspace
    safe_join_workspace(workspace_root, relative_path)
