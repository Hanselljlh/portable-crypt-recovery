"""Tests for the cleanup manifest."""

from portable_crypt_recovery.workspace.cleanup_manifest import (
    add_entry,
    list_entries,
    update_entry_status,
)


def test_add_and_list_entries(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()

    entry = add_entry(ws, "headers/normalized/header_abc.bin", "normalized_header")
    assert entry["relative_path"] == "headers/normalized/header_abc.bin"
    assert entry["category"] == "normalized_header"
    assert entry["status"] == "active"

    entries = list_entries(ws)
    assert len(entries) == 1
    assert entries[0]["relative_path"] == "headers/normalized/header_abc.bin"


def test_add_multiple_entries(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()

    add_entry(ws, "path/a.bin", "type_a")
    add_entry(ws, "path/b.bin", "type_b", description="second file")

    entries = list_entries(ws)
    assert len(entries) == 2
    paths = [e["relative_path"] for e in entries]
    assert "path/a.bin" in paths
    assert "path/b.bin" in paths


def test_update_entry_status(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()

    add_entry(ws, "some/file.txt", "generated_wordlist")
    found = update_entry_status(ws, "some/file.txt", "deleted")
    assert found is True

    entries = list_entries(ws)
    assert entries[0]["status"] == "deleted"


def test_update_nonexistent_entry(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()

    found = update_entry_status(ws, "nonexistent.txt", "deleted")
    assert found is False


def test_list_entries_empty_workspace(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    entries = list_entries(ws)
    assert entries == []


def test_manifest_has_schema_version(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    add_entry(ws, "test.bin", "test")
    import json
    manifest_path = ws / "cleanup" / "cleanup-manifest.json"
    data = json.loads(manifest_path.read_text())
    assert data["schema_version"] == 1
