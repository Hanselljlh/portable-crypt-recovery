# Architecture Overview

## Application Structure

Portable VeraCrypt/TrueCrypt Recovery GUI (PCR) is a portable Python/PySide6 desktop application.

### Source Layout

```
src/portable_crypt_recovery/
├── __init__.py          — App name, version
├── main.py              — Entry point
├── app/
│   ├── application.py   — PySide6 bootstrap
│   ├── app_state.py     — Central in-memory state singleton
│   └── startup.py       — Portable folder layout creation
├── core/
│   ├── atomic_write.py  — Atomic JSON/text writes
│   ├── clipboard.py     — Clipboard utilities
│   ├── ids.py           — Stable ID generation
│   ├── paths.py         — Workspace path helpers
│   ├── platform_info.py — OS/platform summary
│   ├── timestamps.py    — UTC ISO 8601 timestamps
│   └── validation.py    — Path and file validation
├── models/
│   ├── target.py        — Target dataclass
│   ├── header.py        — Header dataclass (512 bytes exactly)
│   ├── job.py           — JobDraft and QueuedJob
│   ├── queue_state.py   — QueueState
│   ├── hashcat_setup.py — HashcatSetup
│   ├── hash_mode_set.py — HashModeSet and HashModeEntry
│   ├── pim_set.py       — PimSet
│   ├── keyfile_set.py   — KeyfileSet and KeyfileEntry
│   ├── password_source.py — PasswordSource
│   ├── report.py        — Report
│   └── diagnostic_bundle.py — DiagnosticBundle
├── workspace/
│   ├── workspace_manager.py   — Create, open, repair workspaces
│   ├── workspace_paths.py     — Workspace folder definitions
│   ├── workspace_schema.py    — JSON schema defaults
│   ├── workspace_state.py     — In-memory workspace state
│   ├── autosave.py            — 60-second periodic queue-state save
│   ├── cleanup_manifest.py    — Cleanup manifest CRUD
│   └── recent_workspaces.py   — Recent workspace list
├── services/
│   ├── hashcat/
│   │   ├── locator.py         — Find hashcat executable
│   │   ├── verifier.py        — Run hashcat --version
│   │   ├── device_scan.py     — Run hashcat --backend-info
│   │   ├── mode_scan.py       — Parse hashcat --help mode list
│   │   ├── command_builder.py — Build argument arrays for jobs
│   │   ├── process_runner.py  — Run hashcat subprocess
│   │   ├── status_parser.py   — Parse --status-json output
│   │   └── fake_hashcat.py    — Test fixture helpers
│   ├── headers/
│   │   ├── extraction.py      — Extract 512-byte candidates from containers
│   │   ├── import_header.py   — Import and normalize user-provided headers
│   │   └── metadata.py        — Save/load header metadata JSON
│   ├── builders/
│   │   ├── hash_mode_builder.py  — Map family+header type to Hashcat modes
│   │   ├── pim_builder.py        — Parse and validate PIM lists
│   │   ├── keyfile_builder.py    — Normalize keyfiles and build combinations
│   │   ├── password_builder.py   — Build password candidate wordlists
│   │   └── final_job_expander.py — Expand mode×PIM×keyfile×password into jobs
│   ├── queue/
│   │   ├── queue_runner.py      — Run jobs one at a time
│   │   ├── runner_lock.py       — Prevent duplicate queue runners
│   │   ├── resume_manager.py    — Find resumable stopped jobs
│   │   └── result_classifier.py — Classify job results (cracked/exhausted/failed)
│   ├── reports/
│   │   ├── report_generator.py  — Generate cracked-job report files
│   │   ├── cracked_package.py   — Assemble recovery package folder
│   │   ├── report_index.py      — Maintain CSV and JSON report indexes
│   │   └── redaction.py         — Mask sensitive fields in report dicts
│   ├── diagnostics/
│   │   ├── diagnostic_bundle.py — Export sanitized diagnostic zip
│   │   ├── log_sanitizer.py     — Strip sensitive lines from logs
│   │   └── workspace_summary.py — Generate workspace statistics text
│   └── logs/
│       ├── app_logger.py        — Rotating app log
│       └── queue_logger.py      — Rotating queue log
└── ui/
    ├── main_window.py       — Main window with navigation and Help menu
    ├── dashboard_view.py    — Workspace/Hashcat status, counts
    ├── targets_view.py      — Target list and Add Volume wizard
    ├── add_volume_wizard.py — Ownership confirmation + header extraction wizard
    ├── jobs_view.py         — Job draft list
    ├── queue_view.py        — Queue controls and progress
    ├── logs_view.py         — Tabbed log viewer
    ├── reports_view.py      — Report list and export
    └── settings_view.py     — Hashcat, workspace, and preference settings
```

## Key Design Rules

1. All Hashcat subprocess calls use `subprocess.Popen(list, ...)` — never `shell=True`.
2. All workspace data stays inside the workspace root — validated with `safe_join_workspace`.
3. All JSON writes use `atomic_write_json` (write temp, rename).
4. All JSON files include `"schema_version": 1`.
5. Job headers must be exactly 512 bytes (validated in `Header.validate_size()`).
6. PIM default is stored as `pim_mode: "default"`, not as 0.
7. Original volumes are opened read-only (`open(..., 'rb')`).
8. PySide6 is lazy-imported inside class bodies so tests run without a display.
9. Passwords are never logged.
10. AppState is a module-level singleton accessed via `get_app_state()`.
