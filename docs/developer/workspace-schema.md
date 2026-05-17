# Workspace Schema

All workspace JSON files include `"schema_version": 1`.

## workspace.json

```json
{
  "schema_version": 1,
  "workspace_id": "workspace_abc123",
  "workspace_name": "my_volume",
  "created_timestamp": "2026-05-17T00:00:00+00:00",
  "last_opened_timestamp": "2026-05-17T00:00:00+00:00",
  "app_version": "0.1.0",
  "created_platform": { ... },
  "notes": ""
}
```

## settings.json

```json
{
  "schema_version": 1,
  "hashcat_path": null,
  "hashcat_path_is_external": false,
  "selected_compute_devices": [],
  "default_queue_behavior_after_crack": "continue_other_uncracked_targets",
  "clipboard_auto_clear_seconds": 60,
  "safety_confirmation_status": false
}
```

## targets/targets.json

```json
{
  "schema_version": 1,
  "targets": [
    {
      "target_id": "target_abc123",
      "display_name": "My Volume",
      "original_path": "/path/to/volume.vc",
      "source_type": "file_container",
      "container_family": "veracrypt",
      "ownership_confirmed": true,
      "notes": "",
      "created_timestamp": "...",
      "updated_timestamp": "..."
    }
  ]
}
```

## queue/queue-state.json

```json
{
  "schema_version": 1,
  "queue_order": ["job_abc123"],
  "current_running_job": null,
  "status": "stopped",
  "jobs": {
    "job_abc123": {
      "job_id": "job_abc123",
      "status": "pending",
      "command_array": ["hashcat", "-m", "29411", ...],
      "pim_mode": "default",
      ...
    }
  }
}
```

## cleanup/cleanup-manifest.json

```json
{
  "schema_version": 1,
  "entries": [
    {
      "relative_path": "headers/normalized/header_abc.bin",
      "category": "normalized_header",
      "description": "",
      "created_by": "extraction",
      "added_timestamp": "...",
      "status": "active"
    }
  ]
}
```

## config/recent-workspaces.json

```json
{
  "schema_version": 1,
  "workspaces": [
    {
      "path": "/absolute/path/to/workspace",
      "name": "my_workspace",
      "last_opened_timestamp": "..."
    }
  ]
}
```

Only stores: path, name, timestamp. No sensitive data.
