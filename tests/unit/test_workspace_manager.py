from portable_crypt_recovery.workspace.workspace_manager import create_or_open_workspace, open_workspace


def test_create_or_open_workspace(tmp_path):
    workspace = create_or_open_workspace(tmp_path / "default", name="default")
    assert workspace.root.exists()
    assert (workspace.root / "workspace.json").exists()
    assert (workspace.root / "settings.json").exists()
    assert (workspace.root / "headers" / "normalized").is_dir()
    reopened = open_workspace(workspace.root)
    assert reopened.record["workspace_id"] == workspace.record["workspace_id"]
