"""Tests for report generation."""

import json

from portable_crypt_recovery.core.ids import new_id
from portable_crypt_recovery.core.timestamps import utc_now_iso
from portable_crypt_recovery.models.header import Header
from portable_crypt_recovery.models.task import QueuedTask
from portable_crypt_recovery.services.headers.metadata import save_header_metadata
from portable_crypt_recovery.services.reports.report_generator import generate_cracked_report
from portable_crypt_recovery.workspace.workspace_manager import create_workspace


def _make_workspace(tmp_path):
    return create_workspace(tmp_path / "workspace", name="test")


def _make_header(ws_root):
    header_id = new_id("header")
    normalized_path = ws_root / "headers" / "normalized" / f"header_{header_id}.bin"
    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    normalized_path.write_bytes(b"\x00" * 512)
    h = Header(
        header_id=header_id,
        target_id="target_001",
        source_type="extracted",
        workspace_relative_path=f"headers/normalized/header_{header_id}.bin",
        size_bytes=512,
        sha256="a" * 64,
        extraction_timestamp=utc_now_iso(),
    )
    save_header_metadata(ws_root, h)
    return h


def _make_cracked_job(header, ws_root):
    task_id = new_id("task")
    session = f"pcr_{task_id}"
    return QueuedTask(
        task_id=task_id,
        target_id="target_001",
        header_id=header.header_id,
        hash_mode_set_id="modeset_001",
        pim_set_id=None,
        keyfile_set_id=None,
        password_source_id="pwsrc_001",
        status="cracked",
        command_array=["hashcat", "-m", "29411", "header.bin"],
        potfile_path=f"hashcat/potfile/{session}.potfile",
        outfile_path=f"hashcat/output/{session}.out",
        log_path=f"hashcat/logs/{session}.log",
        session_name=session,
        hashcat_mode=29411,
        pim_value=None,
        pim_mode="default",
        created_timestamp=utc_now_iso(),
        updated_timestamp=utc_now_iso(),
    )


def test_generate_cracked_report_creates_files(tmp_path):
    ws = _make_workspace(tmp_path)
    header = _make_header(ws.root)
    job = _make_cracked_job(header, ws.root)

    report = generate_cracked_report(
        workspace_root=ws.root,
        job=job,
        cracked_password="S3cr3tP@ss!",
        stats_text="Speed: 100 H/s",
        run_id="run001",
    )

    assert report.report_id.startswith("report_")
    assert report.job_id == job.task_id
    assert report.cracked_password == "S3cr3tP@ss!"

    # Check report folder was created
    pkg_dir = ws.root / report.report_folder
    assert pkg_dir.exists()

    # Check required files
    assert (pkg_dir / "recovered-result.txt").exists()
    assert (pkg_dir / "recovered-result.json").exists()
    assert (pkg_dir / "recovered-result.md").exists()
    assert (pkg_dir / "how-to-open-this-volume.txt").exists()
    assert (pkg_dir / "command-used.txt").exists()
    assert (pkg_dir / "recovery-package-manifest.json").exists()

    # Verify JSON structure
    result_json = json.loads((pkg_dir / "recovered-result.json").read_text())
    assert result_json["cracked_password"] == "S3cr3tP@ss!"
    assert result_json["job_id"] == job.task_id
    assert result_json["schema_version"] == 1


def test_generate_report_adds_to_index(tmp_path):
    from portable_crypt_recovery.services.reports.report_index import list_reports

    ws = _make_workspace(tmp_path)
    header = _make_header(ws.root)
    job = _make_cracked_job(header, ws.root)

    generate_cracked_report(ws.root, job, "mypassword", run_id="r001")
    generate_cracked_report(ws.root, _make_cracked_job(header, ws.root), "pass2", run_id="r002")

    reports = list_reports(ws.root)
    assert len(reports) == 2


def test_report_manifest_has_schema_version(tmp_path):
    ws = _make_workspace(tmp_path)
    header = _make_header(ws.root)
    job = _make_cracked_job(header, ws.root)

    report = generate_cracked_report(ws.root, job, "testpass", run_id="r001")
    pkg_dir = ws.root / report.report_folder
    manifest = json.loads((pkg_dir / "recovery-package-manifest.json").read_text())
    assert manifest["schema_version"] == 1


def test_report_manifest_does_not_expose_original_keyfile_paths(tmp_path):
    """Exported recovery package manifest must not leak original_path for keyfiles."""
    from portable_crypt_recovery.core.atomic_write import atomic_write_json
    from portable_crypt_recovery.core.ids import new_id as _new_id
    from portable_crypt_recovery.models.keyfile_set import KeyfileEntry, KeyfileSet

    ws = _make_workspace(tmp_path)
    header = _make_header(ws.root)

    # Create a task that references a keyfile set
    kf_set_id = _new_id("kfset")
    task_id = _new_id("task")
    session = f"pcr_{task_id}"
    job = QueuedTask(
        task_id=task_id,
        target_id="target_001",
        header_id=header.header_id,
        hash_mode_set_id="modeset_001",
        pim_set_id=None,
        keyfile_set_id=kf_set_id,
        password_source_id="pwsrc_001",
        status="cracked",
        command_array=["hashcat"],
        potfile_path=f"hashcat/potfile/{session}.potfile",
        outfile_path=f"hashcat/output/{session}.out",
        log_path=f"hashcat/logs/{session}.log",
        session_name=session,
        hashcat_mode=29411,
        pim_value=None,
        pim_mode="default",
        created_timestamp=utc_now_iso(),
        updated_timestamp=utc_now_iso(),
    )

    # Write keyfile set JSON with a sensitive original_path
    kf_entry = KeyfileEntry(
        keyfile_id="keyfile_001",
        original_path="C:\\Users\\Alice\\Documents\\secret.key",
        normalized_workspace_path="inputs/keyfiles/normalized/keyfile_001.key",
        size_bytes=32,
        sha256="deadbeef" * 8,
    )
    kf_set = KeyfileSet(set_id=kf_set_id, entries=[kf_entry])
    kf_list_dir = ws.root / "generated" / "keyfile-lists"
    kf_list_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(kf_list_dir / f"{kf_set_id}.json", kf_set.to_dict())

    # Write the normalized keyfile on disk
    norm_dir = ws.root / "inputs" / "keyfiles" / "normalized"
    norm_dir.mkdir(parents=True, exist_ok=True)
    (norm_dir / "keyfile_001.key").write_bytes(b"x" * 32)

    report = generate_cracked_report(ws.root, job, "pass", run_id="r001")
    pkg_dir = ws.root / report.report_folder
    manifest = json.loads((pkg_dir / "recovery-package-manifest.json").read_text())

    assert len(manifest["keyfiles"]) == 1
    kf_entry_out = manifest["keyfiles"][0]

    # Must NOT contain the source-machine path
    assert "original_path" not in kf_entry_out
    assert "Alice" not in json.dumps(kf_entry_out)

    # Must retain identification-friendly fields
    assert kf_entry_out["keyfile_id"] == "keyfile_001"
    assert "sha256" in kf_entry_out
    assert "size_bytes" in kf_entry_out
    assert "package_filename" in kf_entry_out
