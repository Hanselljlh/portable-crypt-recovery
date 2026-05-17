"""Integration test: full workspace flow from creation to queue state."""

import json

from portable_crypt_recovery.core.ids import new_id
from portable_crypt_recovery.core.timestamps import utc_now_iso
from portable_crypt_recovery.models.header import Header
from portable_crypt_recovery.models.job import QueuedJob
from portable_crypt_recovery.models.pim_set import PimSet
from portable_crypt_recovery.models.queue_state import QueueState
from portable_crypt_recovery.services.builders.hash_mode_builder import build_mode_set
from portable_crypt_recovery.services.builders.final_job_expander import expand_jobs
from portable_crypt_recovery.services.builders.password_builder import build_manual_password_source
from portable_crypt_recovery.services.builders.pim_builder import build_default_pim_set
from portable_crypt_recovery.services.headers.metadata import (
    list_header_ids,
    load_header_metadata,
    save_header_metadata,
)
from portable_crypt_recovery.workspace.cleanup_manifest import add_entry, list_entries
from portable_crypt_recovery.workspace.workspace_manager import (
    create_workspace,
    open_workspace,
)


def test_full_workspace_flow(tmp_path):
    # 1. Create workspace
    ws = create_workspace(tmp_path / "test_workspace", name="integration_test")
    assert ws.root.exists()
    assert (ws.root / "workspace.json").exists()

    # 2. Reopen workspace
    ws2 = open_workspace(ws.root)
    assert ws2.record["workspace_id"] == ws.record["workspace_id"]
    assert ws2.name == "integration_test"

    # 3. Create a dummy target record (manual JSON write)
    target_id = new_id("target")
    target_data = {
        "schema_version": 1,
        "target_id": target_id,
        "display_name": "Test Volume",
        "original_path": "/fake/volume.vc",
        "source_type": "file_container",
        "container_family": "veracrypt",
        "ownership_confirmed": True,
        "notes": "",
        "created_timestamp": utc_now_iso(),
        "updated_timestamp": utc_now_iso(),
    }
    targets_file = ws.root / "targets" / "targets.json"
    with targets_file.open("r", encoding="utf-8") as fh:
        targets_data = json.load(fh)
    targets_data["targets"].append(target_data)
    from portable_crypt_recovery.core.atomic_write import atomic_write_json
    atomic_write_json(targets_file, targets_data)

    # 4. Create a dummy 512-byte header and save metadata
    header_id = new_id("header")
    normalized_dir = ws.root / "headers" / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)
    header_file = normalized_dir / f"header_{header_id}.bin"
    header_file.write_bytes(b"\xAB" * 512)

    header = Header(
        header_id=header_id,
        target_id=target_id,
        source_type="extracted",
        workspace_relative_path=f"headers/normalized/header_{header_id}.bin",
        size_bytes=512,
        sha256="deadbeef" * 8,
        extraction_timestamp=utc_now_iso(),
        candidate_type="normal_volume_header",
    )
    save_header_metadata(ws.root, header)

    # Verify we can list and reload the header
    ids = list_header_ids(ws.root)
    assert header_id in ids
    loaded = load_header_metadata(ws.root, header_id)
    assert loaded.size_bytes == 512
    assert loaded.candidate_type == "normal_volume_header"

    # 5. Add a cleanup manifest entry
    add_entry(ws.root, header.workspace_relative_path, "normalized_header", created_by="test")
    entries = list_entries(ws.root)
    assert len(entries) == 1
    assert entries[0]["category"] == "normalized_header"

    # 6. Build a hash mode set
    mode_set = build_mode_set("veracrypt", "normal_volume_header", target_id=target_id, header_id=header_id)
    assert len(mode_set.entries) > 0

    # 7. Build PIM and password source
    pim_set = build_default_pim_set()
    assert pim_set.pim_mode == "default"

    pw_src = build_manual_password_source(["testpass1", "testpass2"], ws.root)
    assert pw_src.candidate_count == 2

    # 8. Expand into queued jobs
    jobs = expand_jobs(
        target_id=target_id,
        header_id=header_id,
        mode_set=mode_set,
        pim_set=pim_set,
        keyfile_sets=None,
        password_source=pw_src,
        workspace_root=ws.root,
    )
    assert len(jobs) == len(mode_set.entries)
    for job in jobs:
        assert job.status == "pending"
        assert job.hashcat_mode in {e.mode for e in mode_set.entries}
        assert job.pim_mode == "default"
        assert job.potfile_path.startswith("hashcat/potfile/")
        assert job.outfile_path.startswith("hashcat/output/")

    # 9. Build queue state and save it
    queue_state = QueueState(
        queue_order=[j.job_id for j in jobs],
        current_running_job=None,
        status="stopped",
        jobs={j.job_id: j for j in jobs},
    )
    queue_path = ws.root / "queue" / "queue-state.json"
    atomic_write_json(queue_path, queue_state.to_dict())

    # Reload and verify
    with queue_path.open("r", encoding="utf-8") as fh:
        saved = json.load(fh)
    assert saved["schema_version"] == 1
    assert saved["status"] == "stopped"
    assert len(saved["jobs"]) == len(jobs)
    assert saved["queue_order"] == [j.job_id for j in jobs]
