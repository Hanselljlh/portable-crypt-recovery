# 12-final-build-plan.md

## Purpose

This file is the final pre-build plan for the Portable VeraCrypt/TrueCrypt Recovery GUI project.

It combines the completed project source files with the final pre-build decisions.

This file should guide GitHub setup, Codex work, phased implementation, testing, packaging, and release preparation.

This file does not redesign earlier sections. It turns the already-decided requirements into a build sequence.

## Build Priority Order

When building the project, apply requirements in this order:

```text
1. 00-final-build-decisions.md
2. 01-basic-program-workings.md through 11-github-codex-build-plan.md
3. This final build plan
4. Implementation-specific decisions made during coding
```

If a conflict appears, use `00-final-build-decisions.md` for final naming, v1 scope limits, future placeholders, and implementation limits.

## Final Naming

App display name:

```text
Portable VeraCrypt/TrueCrypt Recovery GUI
```

Short portable folder name:

```text
PCR
```

Executable name:

```text
PCR
```

Repository name:

```text
portable-crypt-recovery
```

Python package name:

```text
portable_crypt_recovery
```

Reason:

The app should not be named as a general Hashcat GUI. It only supports a focused VeraCrypt and TrueCrypt recovery workflow. The word `Recovery` should remain in the name to make the legitimate purpose clear.

## Core Project Rules

The app must follow these rules throughout the build:

- local desktop GUI only
- legitimate recovery of user-owned or authorized VeraCrypt and TrueCrypt volumes only
- Windows and Linux support
- portable by default
- one chosen workspace per recovery project
- all app-created sensitive and forensic-trail files stay inside the workspace by default
- no use of system temp folders for recovery project data
- no silent upload, transmission, telemetry, or exfiltration
- original volumes are never modified
- original volumes are opened read-only
- Hashcat jobs use extracted or normalized workspace headers only
- Hashcat is the required backend
- John the Ripper is optional future work
- the app does not crack passwords itself
- the app builds, previews, saves, queues, runs, monitors, pauses, resumes, and reports Hashcat jobs
- Hashcat command execution uses argument arrays internally
- command strings are only for preview/export
- one Hashcat job runs at a time
- auto-save every 60 seconds
- immediate save after major changes
- workspace resume after app restart, crash, or interruption
- do not claim secure deletion is guaranteed
- describe cleanup as trace centralization and minimization

## Version 1 Scope

Version 1 supports:

- VeraCrypt file containers
- TrueCrypt file containers
- disk or drive image files
- already extracted header files
- workspace-local normalized 512-byte job headers
- Hashcat setup, verification, and device scan
- hash mode builder
- VeraCrypt PIM builder
- keyfile builder
- password builder
- final job expansion and command builder
- queue runner and resume
- cracked-result reports and recovery folders
- diagnostic bundle export before v1.0.0
- Windows and Linux portable release zips

Version 1 does not support raw physical disk, raw physical drive, or raw physical partition access yet.

Raw physical disk, drive, and partition support should remain visible in the GUI only as disabled planned options marked:

```text
Future
```

## Future Placeholders

The following features should have placeholders, reminders, or disabled GUI labels where appropriate:

- raw physical disk, drive, and partition access
- adjacent PIM range optimization
- recursive keyfile folder scanning
- optional Hashcat auto-download with checksum or signature verification
- optional John the Ripper backend

These placeholders should not block version 1.

## Technology Decisions

Use:

```text
Python 3.12
PySide6
PyInstaller
pytest
ruff or similar linting
JSON workspace files for version 1
MIT License
```

Minimum supported platforms:

```text
Windows 10 64-bit or newer
Ubuntu 22.04 LTS or newer
glibc 2.35 or newer
```

Packaging:

```text
Windows: PyInstaller one-folder build
Linux: plain zip only
Release verification: checksums only for now
Hashcat: not bundled by default in version 1
Hashcat download: no auto-download in version 1
```

## Recommended Repository Layout

```text
portable-crypt-recovery/
  README.md
  LICENSE
  CHANGELOG.md
  SECURITY.md
  CONTRIBUTING.md
  pyproject.toml
  requirements.txt
  requirements-dev.txt
  .gitignore

  .github/
    workflows/
      test.yml
      lint.yml
      build-windows.yml
      build-linux.yml
      release.yml
    ISSUE_TEMPLATE/
      bug_report.md
      packaging_problem.md
      hashcat_setup_problem.md
      queue_resume_problem.md
      report_generation_problem.md
      feature_request.md

  docs/
    project-sources/
      00-final-build-decisions.md
      01-basic-program-workings.md
      02-workspace-and-portability.md
      03-hashcat-setup.md
      04-queue-runner-and-resume.md
      05-header-extraction.md
      06-hash-mode-builder.md
      07-pim-builder.md
      08-keyfile-builder.md
      09-password-builder.md
      10-reports.md
      11-github-codex-build-plan.md
      12-final-build-plan.md

    user-guide/
      getting-started.md
      workspace-cleanup.md
      hashcat-setup.md
      adding-targets.md
      creating-jobs.md
      running-queue.md
      reports.md
      diagnostic-bundle.md
      troubleshooting.md

    developer/
      architecture.md
      workspace-schema.md
      command-array-rules.md
      testing-plan.md
      packaging-plan.md
      release-plan.md

  src/
    portable_crypt_recovery/
      __init__.py
      main.py

      app/
        application.py
        app_state.py
        startup.py

      ui/
        main_window.py
        dashboard_view.py
        targets_view.py
        jobs_view.py
        queue_view.py
        logs_view.py
        reports_view.py
        settings_view.py
        dialogs/
        widgets/

      core/
        ids.py
        paths.py
        atomic_write.py
        validation.py
        timestamps.py
        platform_info.py
        redaction.py
        clipboard.py

      workspace/
        workspace_manager.py
        workspace_schema.py
        workspace_paths.py
        workspace_state.py
        autosave.py
        cleanup_manifest.py
        recent_workspaces.py

      models/
        workspace.py
        target.py
        header.py
        job.py
        queue_state.py
        hashcat_setup.py
        hash_mode_set.py
        pim_set.py
        keyfile_set.py
        password_source.py
        report.py
        diagnostic_bundle.py

      services/
        hashcat/
          locator.py
          verifier.py
          device_scan.py
          mode_scan.py
          command_builder.py
          process_runner.py
          status_parser.py
          fake_hashcat.py

        headers/
          extraction.py
          import_header.py
          metadata.py

        builders/
          hash_mode_builder.py
          pim_builder.py
          keyfile_builder.py
          password_builder.py
          final_job_expander.py

        queue/
          queue_runner.py
          runner_lock.py
          resume_manager.py
          result_classifier.py

        reports/
          report_generator.py
          cracked_package.py
          report_index.py
          redaction.py

        diagnostics/
          diagnostic_bundle.py
          log_sanitizer.py
          workspace_summary.py

        logs/
          app_logger.py
          queue_logger.py

  tests/
    unit/
    integration/
    fixtures/
      fake_hashcat/
      sample_headers/
      sample_keyfiles/
      sample_wordlists/

  scripts/
    run_app.py
    run_tests.py
    build_windows.ps1
    build_linux.sh
    make_release_zip.py
    make_checksums.py

  packaging/
    windows/
      pyinstaller-one-folder.spec
      launcher_template/

    linux/
      pyinstaller-one-folder.spec
      launcher_template/

    portable-template/
      PCR/
        app/
        tools/
          hashcat/
            README-place-hashcat-here.txt
        workspaces/
          default/
        config/
        logs/
        docs/
```

## Portable Folder Layout

The release zip should extract to:

```text
PCR/
  app/
    PCR executable or launcher
    app files

  tools/
    hashcat/
      README-place-hashcat-here.txt

  workspaces/
    default/

  config/
    app-global-settings.json
    recent-workspaces.json

  logs/
    app-startup.log

  docs/
    user-guide/
    safety-notes.txt
```

The default workspace should be:

```text
PCR/workspaces/default/
```

## Workspace Folder Layout

Each workspace should contain:

```text
workspace-name/
  workspace.json
  settings.json

  targets/
    targets.json
    target-notes/
    imported-target-metadata/

  headers/
    imported/
    normalized/
    extracted/
    metadata/

  jobs/
    drafts/
    queued/
    completed/
    failed/
    skipped/
    command-arrays/
    command-previews/

  queue/
    queue-state.json
    runner-lock.json
    autosaves/
    history/

  hashcat/
    sessions/
    restore/
    potfile/
    logs/
    output/

  inputs/
    keyfiles/
      normalized/
      imported-full/
      thumbnails/
      manifests/
    wordlists/
      imported/
      manifests/
    rules/
      imported/
    masks/
      imported/

  generated/
    wordlists/
    masks/
    candidates/
    keyfile-lists/
    pim-lists/
    recipes/
    commands/
    hash-inputs/

  temp/
    active-job/
    staging/

  reports/
    csv/
    json/
    markdown/
    text/
    cracked/
    diagnostics/

  logs/
    app/
    queue/
    errors/

  cleanup/
    cleanup-manifest.json
```

## Implementation Limits

### Password Candidate Limits

Version 1 password candidate generation should use these limits:

```text
More than 100,000 candidates:
  show warning

More than 1,000,000 candidates:
  require confirmation

More than 10,000,000 candidates:
  block unless advanced override is enabled
```

Generated password candidates, generated wordlists, previews, recipes, and temporary chunks must stay inside the workspace.

### Keyfile Combination Limits

Version 1 keyfile combination generation should use these limits:

```text
More than 100 keyfile sets:
  show warning

More than 10,000 keyfile sets:
  require confirmation

More than 100,000 keyfile sets:
  block unless advanced override is enabled
```

Version 1 keyfile folder scanning should include top-level files only.

Recursive keyfile scanning is future work and may be shown as disabled with label:

```text
Future
```

### PIM Handling

Version 1 uses one exact PIM value per Hashcat job variant.

For one exact PIM value, the command builder should set:

```text
--veracrypt-pim-start <value>
--veracrypt-pim-stop <value>
```

Default PIM behavior should be stored as:

```text
pim_mode: default
```

Do not store default PIM as a fake custom value of `0`.

Adjacent PIM range optimization is future work.

### Keyfile Import Defaults

Optional full keyfile copies default to off.

Optional thumbnail generation defaults to off.

If enabled, full copies and thumbnails must stay inside the workspace and be tracked in the cleanup manifest.

Hashcat jobs use normalized workspace-local keyfile copies by default.

### Manual Hashcat Mode Override

Manual Hashcat `-m` override is allowed as an advanced option with a strong warning.

Manual override must still enforce:

- workspace-local normalized headers or workspace-derived hash inputs only
- no original full volumes as Hashcat input
- workspace-local potfile, restore files, logs, output files, and command data
- argument arrays internally
- no unsafe raw shell strings for execution

If the selected manual mode is not reported by the installed Hashcat build, warn the user but allow override if workspace safety rules are satisfied.

### Derived Hash Input Files

If a Hashcat mode requires a derived `$truecrypt$` or `$veracrypt$` text input instead of a raw 512-byte header file, create that file inside:

```text
generated/hash-inputs/
```

Rules:

- derive only from the normalized workspace header
- do not read the original volume again
- do not use system temp folders
- track derived hash input files in the cleanup manifest
- treat derived hash input files as sensitive recovery strategy data

### Reports

Report regeneration creates versioned copies by default.

Overwriting existing reports requires user confirmation.

Reports stay inside the workspace by default.

External report exports require warning and cleanup manifest entry.

### Clipboard

Copied recovered passwords auto-clear from the clipboard after 60 seconds by default.

The user may disable clipboard auto-clear in settings.

The GUI hides recovered passwords by default and requires user action to reveal or copy them.

## Branch Strategy

Recommended branches:

```text
main
dev
phase-01-repo-foundation
phase-02-app-shell
phase-03-workspace
...
```

Rules:

- `main` contains stable tested releases.
- `dev` contains the next working version.
- Each phase is built in its own branch or pull request.
- Merge a phase only after tests and manual checks pass.
- Do not redesign earlier systems unless a bug requires it.
- For solo development, direct commits to `dev` are acceptable, but each phase should still be a separate commit group.

## Codex Working Rules

Codex should follow these rules:

- read `docs/project-sources/` before editing
- treat source files as requirements
- apply `00-final-build-decisions.md` first when resolving conflicts
- build one phase at a time
- keep commits small
- keep GUI code separate from backend logic
- write backend tests before or during each phase
- use fake Hashcat tests before real Hashcat tests
- keep Windows and Linux path behavior in mind from the start
- never use unsafe raw shell strings for Hashcat execution
- store command execution internally as argument arrays
- keep command previews separate from executable command arrays
- do not write sensitive project data outside the workspace by default
- do not use system temp folders for recovery project data
- do not modify original VeraCrypt or TrueCrypt volumes
- do not run Hashcat against original full volumes
- never silently upload, transmit, or exfiltrate project data

## Phase 1: Repository Foundation

Goal:

Create the GitHub repository structure and basic Python project.

Build:

- repository skeleton
- MIT LICENSE
- README.md
- CHANGELOG.md
- SECURITY.md
- CONTRIBUTING.md
- pyproject.toml
- requirements files
- `src/portable_crypt_recovery/`
- tests folder
- docs folder
- scripts folder
- basic app entry point

Acceptance tests:

- project installs in editable mode
- unit test runner works
- app entry point starts and exits cleanly
- package imports as `portable_crypt_recovery`
- no GUI feature is required yet

Do not build yet:

- Hashcat runner
- header extraction
- password generation
- reports
- packaging

## Phase 2: Core App Shell

Goal:

Create the basic local GUI shell.

Build:

- PySide6 app startup
- main window
- left sidebar navigation
- Dashboard placeholder
- Targets placeholder
- Jobs placeholder
- Queue placeholder
- Logs placeholder
- Reports placeholder
- Settings placeholder
- Help menu placeholder
- Exit handling

Required screens:

```text
Dashboard
Targets
Jobs
Queue
Logs
Reports
Settings
```

Acceptance tests:

- app launches on Windows development system
- app launches on Linux development system
- all screens can be opened
- no crash when switching screens
- window title uses `Portable VeraCrypt/TrueCrypt Recovery GUI`
- executable/build target uses `PCR`
- no recovery features are active yet

## Phase 3: Workspace System

Goal:

Create, open, validate, and repair workspaces.

Build:

- workspace manager
- default portable workspace creation
- browse for workspace
- recent workspaces
- `workspace.json`
- `settings.json`
- required folder creation
- workspace path validation
- relative path handling
- external path marking
- disabled future labels for raw disk/partition sources where needed

Acceptance tests:

- new default workspace can be created at `PCR/workspaces/default/`
- existing workspace can be reopened
- missing safe folders can be repaired
- workspace-internal paths are stored relatively where possible
- sensitive project folders are not created outside workspace
- recent workspace data does not contain sensitive recovery data
- no system temp folder is used for workspace operations

## Phase 4: Data Models and Schemas

Goal:

Create stable internal records before building feature screens.

Build JSON-backed models for:

- workspace
- target
- header
- job draft
- queued job
- queue state
- Hashcat setup
- hash mode set
- PIM set
- keyfile metadata
- keyfile group
- password source
- report
- cleanup manifest entry
- diagnostic bundle metadata

Each model should include:

- schema version
- stable ID
- timestamps
- workspace-relative paths where possible
- notes where useful
- safe unknown-field handling for future schema updates

Acceptance tests:

- models serialize to JSON
- models load from JSON
- unknown future fields do not break loading
- required fields are validated
- invalid paths are rejected where needed
- sensitive fields are not accidentally written to global app config

## Phase 5: Save, Autosave, Logs, and Cleanup Manifest

Goal:

Create the foundation for safe state tracking.

Build:

- atomic JSON write helper
- manual save
- autosave every 60 seconds
- immediate save hooks
- app logs
- queue logs
- error logs
- cleanup manifest
- external-location warning helper
- app-global config with only non-sensitive settings

Autosave folder:

```text
queue/autosaves/
```

Cleanup manifest path:

```text
cleanup/cleanup-manifest.json
```

Acceptance tests:

- atomic save writes inside workspace only
- autosave files are created inside workspace
- immediate save hooks are callable
- cleanup manifest records app-created files
- external paths are marked external and non-portable
- logs stay inside workspace or portable app startup logs as appropriate
- system temp folder is not used for recovery project data

## Phase 6: Hashcat Setup

Goal:

Locate, verify, and remember Hashcat.

Build:

- Hashcat setup screen
- portable tools folder detection
- browse for Hashcat executable
- custom tools folder support
- optional PATH detection
- open official Hashcat download page
- `hashcat --version` verification
- `hashcat --backend-info` device scan or supported equivalent
- device selection storage
- repair missing Hashcat path
- installed Hashcat mode-list scan for later builders

Version 1 rules:

- do not bundle Hashcat by default
- do not auto-download Hashcat
- user downloads Hashcat manually
- app may open the official Hashcat download page

Expected executable names:

```text
Windows: hashcat.exe
Linux: hashcat or hashcat.bin
```

Acceptance tests:

- fake Hashcat `--version` passes verification
- bad executable fails verification
- fake device scan output can be parsed
- mode list can be cached for later mode support checks
- Hashcat path inside portable folder can be stored relatively
- external Hashcat path is marked non-portable
- Hashcat checks use argument arrays
- Hashcat errors are visible and logged

## Phase 7: Target and Header Workflow

Goal:

Add one volume at a time and create normalized 512-byte job headers.

Build:

- Add Volume wizard
- ownership confirmation
- source type selection
- container family selection
- volume possibility selection
- valid header candidate checkboxes
- review before extraction
- read-only extraction from file containers and disk/drive image files
- already-extracted header import
- target metadata
- header metadata
- normalized 512-byte job headers
- disabled `Future` labels for raw physical disk/drive/partition access

Version 1 supported source categories:

```text
File container
Non-system disk/drive image
System disk/drive image
Already extracted header
Unknown / not sure
```

Version 1 planned but disabled source categories:

```text
Non-system physical partition/device: Future
System physical partition/drive/device: Future
Raw physical disk/drive access: Future
```

Required extraction candidates:

```text
normal_volume_header: offset 0, length 512
hidden_volume_header: offset 65536, length 512
normal_system_header: offset 31744, length 512
hidden_system_candidate: separate system candidate record with warning
```

Header import rules:

```text
If exactly 512 bytes:
  import and normalize as 512-byte job header.

If larger than 512 bytes and no larger than 128 KiB:
  import and normalize selected 512-byte candidate.

If larger than 128 KiB:
  reject as too large for header import.
```

Acceptance tests:

- original source is opened read-only
- original source is not modified
- extracted headers are exactly 512 bytes
- normalized job headers are exactly 512 bytes
- imported headers larger than 128 KiB are rejected
- jobs cannot use original full volume paths
- header metadata is saved
- cleanup manifest is updated
- raw physical device options are visible only as disabled `Future` labels

## Phase 8: Hash Mode Builder

Goal:

Build valid Hashcat mode sets for selected headers.

Build:

- hash mode builder screen
- VeraCrypt / TrueCrypt / Both selection
- source and header metadata review
- encryption selection
- hash / PRF / KDF selection
- VeraCrypt Argon2id handling where supported by installed Hashcat
- Try Every Valid VeraCrypt / TrueCrypt Mode option
- OR-style mode entries
- invalid-combination filtering
- current and legacy mode mapping
- installed Hashcat mode support check
- manual `-m` override with warning
- mode preview
- saved mode set metadata

Required beginner option:

```text
Try Every Valid VeraCrypt / TrueCrypt Mode
```

Derived input rule:

If selected Hashcat mode requires `$truecrypt$` or `$veracrypt$` text input, later command generation must create it in:

```text
generated/hash-inputs/
```

Acceptance tests:

- TrueCrypt cannot use VeraCrypt-only PRFs or ciphers
- VeraCrypt-only options are not generated for TrueCrypt jobs
- normal and hidden non-system headers use non-system modes
- system headers use system / boot modes
- hidden system candidate is not presented as a normal hidden volume
- duplicate generated modes are removed
- unsupported installed-Hashcat modes are shown as skipped, not silently hidden
- manual override still uses workspace-local input only
- manual override warns if mode is not reported by installed Hashcat

## Phase 9: PIM Builder

Goal:

Create VeraCrypt PIM sets.

Build:

- PIM builder screen
- default PIM option
- exact PIM input
- comma-separated input
- newline-separated input
- range input
- range expansion
- deduplication
- sorting
- preview before save
- PIM metadata
- PIM list files
- job draft update
- future placeholder for adjacent PIM range optimization

Rules:

- PIM applies to VeraCrypt only
- TrueCrypt jobs do not use PIM
- default PIM is stored as `pim_mode: default`
- `0` is rejected as a custom PIM value
- version 1 uses one exact PIM per job variant

Acceptance tests:

- `789-805` expands correctly
- mixed commas and newlines parse correctly
- duplicates are removed
- values are sorted ascending
- invalid values are rejected
- large lists show warnings
- PIM files stay inside `generated/pim-lists/`
- adjacent PIM optimization is present only as future placeholder

## Phase 10: Keyfile Builder

Goal:

Import, normalize, and group keyfiles.

Build:

- no-keyfiles mode
- exact selected keyfiles
- folder as one keyfile set
- folder combination generation
- top-level folder scan only for v1
- disabled `Future` label for recursive folder scanning
- normalized keyfile copies
- optional full-copy import, default off
- optional workspace-local thumbnails, default off
- keyfile metadata
- keyfile group metadata
- keyfile set metadata
- combination preview
- keyfile combination limits
- dedupe across groups
- job draft update

Normalization rule:

```text
If keyfile is 1,048,576 bytes or smaller:
  copy the entire file byte-for-byte.

If keyfile is larger than 1,048,576 bytes:
  copy only the first 1,048,576 bytes byte-for-byte.
```

Combination limits:

```text
More than 100 keyfile sets:
  show warning

More than 10,000 keyfile sets:
  require confirmation

More than 100,000 keyfile sets:
  block unless advanced override is enabled
```

Acceptance tests:

- original keyfiles are not modified
- normalized keyfiles are workspace-local
- large keyfiles are capped to first 1 MiB
- small keyfiles are copied exactly
- keyfile combinations are combinations, not permutations
- duplicate combinations are removed
- recursive folder scan is disabled and marked `Future`
- Hashcat job paths never use original keyfile paths by default
- optional full copies default off
- optional thumbnails default off
- keyfile contents are not printed in logs

## Phase 11: Password Builder

Goal:

Create password candidate sources.

Build:

- segment builder
- manual password list
- imported wordlist copy
- external wordlist reference
- ordered segments
- OR variants per segment
- exact text variants
- case variants
- same characters unknown order
- same characters unknown order plus case variants
- manual variant lists
- pattern token expansion
- segment filters before generation
- candidate count preview
- large candidate limits
- small-list candidate review
- generated wordlist storage
- password recipe metadata
- job draft update

Required user-facing pattern token:

```text
?C = any letter, lowercase or uppercase
```

Do not expose `?1` as a normal user-facing token.

Candidate limits:

```text
More than 100,000 candidates:
  show warning

More than 1,000,000 candidates:
  require confirmation

More than 10,000,000 candidates:
  block unless advanced override is enabled
```

Acceptance tests:

- segment order is preserved
- variant order is preserved
- final duplicate cleanup preserves first-seen order
- candidate count preview works
- large candidate warnings appear
- advanced override is required above hard limit
- generated wordlists stay in `generated/wordlists/`
- temporary candidate chunks stay inside workspace
- external wordlists are marked external and non-portable
- system temp folder is not used

## Phase 12: Final Job Expansion and Command Builder

Goal:

Combine hash modes, PIMs, keyfiles, and password sources into runnable queued jobs.

Build:

- final job expansion screen
- job count preview
- VeraCrypt and TrueCrypt split counts
- Hashcat argument array builder
- command preview generator
- workspace-local input validation
- workspace-derived hash input generation in `generated/hash-inputs/`
- workspace-local output path creation
- queue job creation
- command array save
- command preview save

Each queued job should include:

- normalized header or workspace-derived Hashcat input
- Hashcat mode
- PIM option if VeraCrypt and custom PIM applies
- keyfile option if keyfiles apply
- password source
- session name placeholder
- restore path placeholder
- potfile path
- outfile path
- log path
- status log path

Required command behavior:

```text
Internal command format: argument array.
Human-readable command string: preview/export only.
```

Acceptance tests:

- generated jobs use only workspace-local headers or workspace-derived hash inputs
- generated jobs use only normalized workspace keyfiles
- generated jobs use workspace-local potfile, restore, logs, and output paths
- command arrays are valid lists
- command previews are not used for execution
- external wordlists are allowed only when explicitly selected and marked
- derived hash input files are written to `generated/hash-inputs/`
- queue job count matches preview

## Phase 13: Queue Runner and Resume

Goal:

Run one Hashcat job at a time and preserve resume state.

Build:

- queue runner
- runner lock
- start queue
- pause now
- pause after current job
- stop and save
- stop and discard
- resume
- skip selected job
- restart selected job
- unique session names per run
- workspace-local restore files
- workspace-local potfile
- workspace-local logs
- workspace-local output files
- status JSON parsing
- result classification
- crash recovery prompt

Final runner statuses:

```text
pending
running
paused
stopped_saved
cracked
exhausted
failed
skipped
```

Queue behavior after successful crack:

```text
Continue with other uncracked targets
Stop entire queue
```

Acceptance tests:

- only one job can run at a time
- runner lock blocks duplicate runners for one workspace
- each run attempt gets a unique session name
- Pause Now pauses active process when supported
- Pause After Current does not interrupt active job
- Stop and Save preserves restore data when possible
- Resume uses restore data and user confirmation
- crash recovery does not auto-start Hashcat
- cracked target skips remaining pending jobs for same target/header
- next job does not start until current result is classified and saved

Fake Hashcat should simulate:

- `--version`
- `--backend-info`
- mode list output
- running status output
- cracked result
- exhausted result
- failed result
- restore behavior

## Phase 14: Reports and Cracked-Result Packages

Goal:

Generate useful reports immediately when a job is cracked.

Build:

- live cracked-result reporting
- non-blocking cracked popup
- queue row report actions
- Reports screen result viewer
- per-cracked-job recovery folder
- `recovered-result.txt`
- `recovered-result.json`
- `recovered-result.md`
- `stats.txt`
- `command-used.txt`
- `how-to-open-this-volume.txt`
- `recovery-package-manifest.json`
- CSV cracked-results index
- JSON report index
- redacted reports
- report export warning
- report regeneration with versioned copies by default
- overwrite confirmation for regenerated reports
- clipboard auto-clear after password copy

Per-cracked-job folder:

```text
reports/cracked/job_<job_id>_run_<run_id>/
```

Minimum files:

```text
recovered-result.txt
recovered-result.json
recovered-result.md
recovery-package-manifest.json
how-to-open-this-volume.txt
job-header-512.bin
command-used.txt
stats.txt
keyfiles/
```

Rules:

- save raw cracked result first
- never lose a cracked result because report generation failed
- copy only the successful normalized job header
- copy only successful normalized keyfiles
- do not copy unrelated wordlists or candidate lists
- reports stay inside workspace by default
- passwords are hidden by default in the GUI
- copied passwords auto-clear after 60 seconds by default

Acceptance tests:

- cracked job creates minimum report package
- report generation failure does not erase cracked result
- CSV index updates
- report index updates
- recovery folder contains only successful-job materials
- password reveal is user-controlled
- clipboard clears copied password after 60 seconds by default
- redacted report removes selected sensitive fields
- report regeneration creates versioned copy by default
- external export warns and records cleanup manifest entry

## Phase 15: Diagnostic Bundle Export

Goal:

Add a safe support bundle before v1.0.0 so non-technical users can report issues without sharing secrets.

Build:

- Help → Export Diagnostic Bundle
- diagnostic bundle preview
- redaction-by-default
- sanitized app logs
- sanitized error logs
- workspace summary
- app version
- OS version
- workspace schema version
- Hashcat version if configured
- device summary if scanned
- missing-path summary
- settings summary without sensitive strategy data

Diagnostic bundle must exclude by default:

- passwords
- cracked results
- headers
- keyfiles
- potfiles
- generated wordlists
- generated candidate chunks
- Hashcat output containing recovered secrets
- private notes unless the user explicitly includes them
- original volumes

Suggested diagnostic output folder:

```text
reports/diagnostics/
```

Suggested filename:

```text
diagnostic_bundle_<timestamp>.zip
```

Acceptance tests:

- diagnostic bundle is redacted by default
- no headers are included
- no keyfiles are included
- no cracked result files are included
- no potfiles are included
- no generated wordlists are included
- sanitized logs are included
- external export is warned and recorded

## Phase 16: Packaging and Release Zips

Goal:

Create portable release folders for Windows and Linux.

Build:

- PyInstaller one-folder build for Windows
- PyInstaller one-folder build for Linux
- plain zip release for Windows
- plain zip release for Linux
- portable folder template using `PCR/`
- Hashcat placeholder README
- checksums file
- release scripts

Version 1 packaging rules:

- do not bundle Hashcat by default
- do not include sample passwords
- do not include sample cracked results
- do not include real headers
- do not include real keyfiles
- do not include real potfiles
- do not include real user workspaces
- do not write user data into app folder outside chosen workspace

Release examples:

```text
PCR-Windows-x64-v0.1.0.zip
PCR-Linux-x64-v0.1.0.zip
checksums.txt
```

Acceptance tests:

- Windows zip extracts and launches on Windows 10 64-bit or newer
- Linux zip extracts and launches on Ubuntu 22.04 LTS or newer
- default workspace is created
- Hashcat missing warning appears cleanly
- user can browse to Hashcat
- app paths work from a folder with spaces
- app paths work after moving the portable folder
- checksums.txt is generated for release zips

## Phase 17: Windows and Linux Testing

Goal:

Confirm the same workspace rules and basic workflows on both platforms.

Windows test checklist:

- launch app from extracted zip
- create default workspace
- create custom workspace
- move portable folder and reopen workspace
- browse to `hashcat.exe`
- verify fake or real Hashcat with `--version`
- scan devices
- extract test header from sample file container
- extract test header from sample disk image file
- import a 512-byte header
- reject oversized imported header
- create hash mode set
- create PIM set
- import normalized keyfile
- generate small password wordlist
- create queued job with fake Hashcat
- run fake cracked job
- generate report package
- copy password and confirm clipboard auto-clear behavior
- export redacted diagnostic bundle
- close and reopen app
- confirm saved state loads

Linux test checklist:

- launch app from extracted zip or launcher
- check executable permissions
- create default workspace
- create custom workspace
- move portable folder and reopen workspace
- browse to `hashcat` or `hashcat.bin`
- verify fake or real Hashcat with `--version`
- scan devices
- extract test header from sample file container
- extract test header from sample disk image file
- import a 512-byte header
- reject oversized imported header
- create hash mode set
- create PIM set
- import normalized keyfile
- generate small password wordlist
- create queued job with fake Hashcat
- run fake cracked job
- generate report package
- copy password and confirm clipboard auto-clear behavior
- export redacted diagnostic bundle
- close and reopen app
- confirm saved state loads

Cross-platform checks:

- workspace-relative paths survive moves when possible
- external paths are marked and repairable
- no system temp folder is used for recovery data
- raw physical disk/partition options are disabled and marked `Future`
- generated files stay inside workspace by default

## Phase 18: User Testing and Issue Reporting

Goal:

Prepare the project for early real-user testing without losing safety and trace-control rules.

Build or finalize:

- README quick start
- user guide basics
- safety notes
- workspace cleanup guide
- Hashcat setup guide
- troubleshooting guide
- issue templates
- diagnostic bundle instructions
- known limitations list
- future roadmap list

Known limitations for v1:

- raw physical disk, drive, and partition access is future work
- adjacent PIM range optimization is future work
- recursive keyfile folder scanning is future work
- Hashcat auto-download is future work
- John the Ripper backend is future work

Acceptance tests:

- README explains app purpose clearly
- README does not present the app as a general Hashcat GUI
- safety notes explain authorized recovery only
- cleanup guide explains centralization without promising secure deletion
- issue templates ask users not to upload secrets
- diagnostic guide explains redaction defaults
- known limitations match v1 scope

## First Codex Prompt

Use this prompt to start the implementation in Codex:

```text
We are building the Portable VeraCrypt/TrueCrypt Recovery GUI project.

Read all files in docs/project-sources before coding.

Highest priority source file:
00-final-build-decisions.md

Then follow:
01-basic-program-workings.md through 12-final-build-plan.md

Build Phase 1 only:
Repository Foundation.

Do not build later features yet.
Do not redesign earlier decisions.
Use Python 3.12, PySide6, PyInstaller, pytest, and JSON workspace files for version 1.

Final naming:
App display name: Portable VeraCrypt/TrueCrypt Recovery GUI
Portable folder/executable short name: PCR
Repository: portable-crypt-recovery
Python package: portable_crypt_recovery

Core rules:
- local GUI only
- authorized VeraCrypt/TrueCrypt recovery only
- Hashcat is required backend but is not bundled in v1
- no Hashcat auto-download in v1
- no system temp folders for recovery project data
- commands must be argument arrays internally
- original volumes must never be modified
- jobs must use workspace-local normalized headers only

For Phase 1, create the repository foundation, package skeleton, docs folders, tests folder, scripts folder, README, LICENSE, and basic entry point.

Stop after Phase 1 and report what files were created and how to run tests.
```

## Phase Completion Rule

At the end of each phase, Codex should provide:

```text
Phase completed:
Files created or changed:
Tests added:
Tests run:
Manual checks needed:
Known issues:
Next recommended phase:
```

Do not start the next phase until the previous phase is tested and accepted.

## Final Build Readiness

The design is ready to start implementation after this file is added to project sources.

The first build phase should be repository foundation only.

