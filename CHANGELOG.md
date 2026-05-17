# Changelog

All notable changes to Portable VeraCrypt/TrueCrypt Recovery GUI (PCR) are documented here.

## [0.1.0] - 2026-05-17

### Added

- Initial release of Portable VeraCrypt/TrueCrypt Recovery GUI
- Portable folder layout (PCR/) with workspace, tools, config, logs
- Workspace creation, opening, and repair
- Header extraction from file containers and disk images (512-byte candidates: normal, hidden, system)
- Header import with 512-byte normalization
- Hash mode builder mapping VeraCrypt and TrueCrypt container families to Hashcat mode numbers
- PIM parser and expansion (comma/newline separated integers and ranges)
- Keyfile normalization (first 1 MiB rule) and combination builder
- Password candidate builder (manual list, wordlist import, segment-based generation)
- Final job expander combining HashModeSet × PimSet × KeyfileSet × PasswordSource
- Queue runner with pause, resume, stop-and-save, stop-and-discard controls
- Runner lock to prevent duplicate queue instances per workspace
- Resume manager for Hashcat --restore sessions
- Result classifier reading potfile/outfile after job completion
- Cracked report generator with recovery package folder
- Report index (CSV and JSON)
- Diagnostic bundle export (sanitized logs, workspace summary, no sensitive data)
- App and queue rotating file loggers
- PySide6 GUI with Dashboard, Targets, Jobs, Queue, Logs, Reports, Settings views
- Help menu with user guide, workspace/logs folders, diagnostic export, GitHub link
- Autosave loop (60-second periodic queue-state.json save)
- Cleanup manifest for workspace-local file tracking
- Recent workspaces list (path, name, timestamp only — no sensitive data)
- Central AppState singleton for in-memory application state
- All Hashcat invocations use subprocess argument arrays (never shell=True)
- Workspace-relative path storage for all internal file references
- Atomic JSON writes for all persistent state files
- Schema version 1 on all JSON files
- Clipboard auto-clear after 60 seconds (configurable)
- Passwords hidden by default in UI with Reveal button
