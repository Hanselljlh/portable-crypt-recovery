# 11-github-codex-build-plan.md

## Purpose

This step defines the GitHub and Codex build plan for the Portable VeraCrypt/TrueCrypt Recovery GUI project.

The goal is to turn the completed design source files into a practical phased build plan that Codex can follow without rebuilding from scratch after each phase.

This step does not redesign earlier sections.

Earlier source files are treated as decided:

```text
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
```

The app should be built in phases.

Each phase should build on the previous phase.

Each phase should be tested before moving to the next phase.

## Final Project Decisions For Build Planning

These decisions are now set for the initial build plan:

```text
License: MIT License
GUI toolkit: PySide6
Packaging tool: PyInstaller
Linux release format: plain zip only
Windows packaging format: PyInstaller one-folder build
Minimum Python version: Python 3.12
Minimum Windows version: Windows 10 64-bit
Minimum Linux target: Ubuntu 22.04 LTS or newer, glibc 2.35 or newer
Release verification: checksums only for now
Diagnostic bundle export: include before v1.0.0, redacted by default
Hashcat bundling: do not bundle Hashcat by default in version 1
Hashcat download: do not auto-download Hashcat in version 1
John the Ripper: optional later, not required for version 1
```

## License Decision

Use:

```text
MIT License
```

Reason:

```text
Hashcat is MIT licensed.
This GUI is intended to be a local wrapper and manager around Hashcat.
MIT keeps the project permissive, simple, easy to package, and easy for contributors to understand.
```

The GUI does not need to use the same license solely because it calls Hashcat as an external backend, but MIT is the best practical fit for this project.

The repository should include:

```text
LICENSE
```

with the standard MIT License text.

## Core Build Rule

Codex should build the project in small working layers.

The practical build order should be:

```text
1. Repository foundation
2. Core app shell
3. Workspace system
4. Data models and schemas
5. Save, autosave, logs, and cleanup manifest
6. Hashcat setup
7. Target and header workflow
8. Hash mode builder
9. PIM builder
10. Keyfile builder
11. Password builder
12. Final job expansion and command builder
13. Queue runner and resume
14. Reports and cracked-result packages
15. Diagnostic bundle export
16. Packaging and release zips
17. Windows and Linux testing
18. User testing and issue reporting
```

This order lets Codex build the base systems first, then attach each feature to stable workspace, schema, and test code.

## Recommended Technology Stack

Use:

```text
Python 3.12
PySide6
PyInstaller
pytest
ruff or similar linting
JSON for version 1 workspace files
```

Python 3.12 is the minimum supported Python version for development and packaging.

PySide6 is the chosen GUI toolkit.

PyInstaller is the chosen packaging tool.

The app should keep backend logic separate from GUI code.

Core backend code should be testable without launching the GUI.

## GitHub Repository Layout

Suggested repository layout:

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

      workspace/
        workspace_manager.py
        workspace_schema.py
        workspace_paths.py
        workspace_state.py
        autosave.py
        cleanup_manifest.py
        recent_workspaces.py

      models/
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

## Git Branch Strategy

Use a simple branch strategy.

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

```text
main contains stable tested releases.
dev contains the next working version.
Each phase is built in its own branch or pull request.
Merge a phase only after tests and manual checks pass.
Do not rewrite earlier systems unless a bug requires it.
```

For a solo build, direct commits to `dev` are acceptable, but each phase should still be a separate commit group.

## Codex Working Rules

Codex should follow these rules:

```text
Read the source files in docs/project-sources before editing.
Treat earlier source files as requirements.
Do not redesign earlier decisions unless asked.
Build one phase at a time.
Prefer small commits.
Keep GUI code separate from backend logic.
Write tests for backend logic before or during each phase.
Do not use unsafe raw shell strings for Hashcat execution.
Store Hashcat commands internally as argument arrays.
Do not write sensitive project data outside the workspace.
Do not use system temp folders for recovery project data.
Do not modify original VeraCrypt or TrueCrypt volumes.
Do not run Hashcat against original full volumes.
Use fake Hashcat tests before real Hashcat tests.
Keep Windows and Linux paths in mind from the start.
```

## Phase 1: Repository Foundation

Goal:

```text
Create the GitHub repository structure and basic Python project.
```

Codex should build:

```text
pyproject.toml
requirements.txt
requirements-dev.txt
src/portable_crypt_recovery/
tests/
docs/
scripts/
basic README
MIT LICENSE file
basic app entry point
```

Acceptance tests:

```text
Project installs in editable mode.
Unit test runner works.
App entry point starts and exits cleanly.
No GUI feature is required yet.
```

Do not build:

```text
Hashcat runner
header extraction
password generation
reports
packaging
```

## Phase 2: Core App Shell

Goal:

```text
Create the basic local GUI shell.
```

Codex should build:

```text
Main window
Left sidebar navigation
Dashboard screen placeholder
Targets screen placeholder
Jobs screen placeholder
Queue screen placeholder
Logs screen placeholder
Reports screen placeholder
Settings screen placeholder
Basic app menu
Exit handling
```

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

```text
App launches on Windows and Linux development systems.
All screens can be opened.
No crash when switching screens.
No recovery functions are active yet.
```

## Phase 3: Workspace System

Goal:

```text
Create, open, validate, and repair workspaces.
```

Codex should build:

```text
workspace manager
default portable workspace creation
browse for workspace
recent workspaces
workspace.json
settings.json
required folder creation
workspace path validation
relative path handling
external path marking
```

Required default portable structure:

```text
PCR/
  app/
  tools/hashcat/
  workspaces/default/
  config/
  logs/
  docs/
```

Required workspace folders:

```text
targets/
headers/
jobs/
queue/
hashcat/
inputs/
generated/
temp/
reports/
logs/
cleanup/
```

Acceptance tests:

```text
New default workspace can be created.
Existing workspace can be reopened.
Missing safe folders can be repaired.
Workspace-internal paths are stored relatively where possible.
Sensitive project folders are not created outside the workspace.
Recent workspace data does not contain sensitive recovery data.
```

## Phase 4: Data Models and Schemas

Goal:

```text
Create stable internal records before building feature screens.
```

Codex should build models for:

```text
workspace
target
header
job draft
queued job
queue state
Hashcat setup
hash mode set
PIM set
keyfile metadata
keyfile group
password source
report
cleanup manifest entry
diagnostic bundle metadata
```

Use JSON files for version 1.

Each model should include:

```text
schema_version
stable ID
timestamps
workspace-relative paths when possible
notes where useful
```

Acceptance tests:

```text
Models serialize to JSON.
Models load from JSON.
Unknown future fields do not break loading.
Required fields are validated.
Invalid paths are rejected where needed.
```

## Phase 5: Save, Autosave, Logs, and Cleanup Manifest

Goal:

```text
Create the foundation for safe state tracking.
```

Codex should build:

```text
atomic JSON write helper
manual save
autosave every 60 seconds
immediate save hooks
app logs
queue logs
error logs
cleanup manifest
external-location warning helper
```

Autosave should write inside:

```text
queue/autosaves/
```

Cleanup manifest path:

```text
cleanup/cleanup-manifest.json
```

Acceptance tests:

```text
Atomic save writes inside workspace only.
Autosave files are created inside workspace.
Cleanup manifest records app-created files.
External paths are marked as external.
Logs stay inside workspace or portable app logs as appropriate.
System temp folder is not used for recovery project data.
```

## Phase 6: Hashcat Setup

Goal:

```text
Locate, verify, and remember Hashcat.
```

Codex should build:

```text
Hashcat setup screen
portable tools folder detection
browse for Hashcat executable
custom tools folder support
optional PATH detection
open official Hashcat download page
hashcat --version verification
hashcat --backend-info device scan
device selection storage
repair missing Hashcat path
```

Version 1 rule:

```text
Do not auto-download Hashcat.
```

Expected executable names:

```text
Windows: hashcat.exe
Linux: hashcat or hashcat.bin
```

Acceptance tests:

```text
Fake Hashcat --version passes verification.
Bad executable fails verification.
Device scan output can be parsed from fake Hashcat.
Hashcat path inside portable folder can be stored relatively.
External Hashcat path is marked non-portable.
Hashcat checks use argument arrays.
```

## Phase 7: Target and Header Workflow

Goal:

```text
Add one volume at a time and create normalized 512-byte job headers.
```

Codex should build:

```text
Add Volume wizard
ownership confirmation
source type selection
container family selection
volume possibility selection
valid header candidate checkboxes
review before extraction
read-only extraction
already-extracted header import
target metadata
header metadata
normalized 512-byte job headers
```

Supported source categories:

```text
File container
Non-system partition/device
Non-system disk/drive image
System partition/drive/device
System disk/drive image
Already extracted header
Unknown / not sure
```

Required extraction candidates:

```text
normal_volume_header: offset 0, length 512
hidden_volume_header: offset 65536, length 512
normal_system_header: offset 31744, length 512
hidden_system_candidate: separate system candidate record
```

Acceptance tests:

```text
Original source is opened read-only.
Original source is not modified.
Extracted headers are exactly 512 bytes.
Normalized job headers are exactly 512 bytes.
Imported headers larger than 128 KiB are rejected.
Jobs cannot use original full volume paths.
Header metadata is saved.
Cleanup manifest is updated.
```

## Phase 8: Hash Mode Builder

Goal:

```text
Build valid Hashcat mode sets for selected headers.
```

Codex should build:

```text
hash mode builder screen
VeraCrypt / TrueCrypt / Both selection
source and header metadata review
encryption selection
hash / PRF / KDF selection
try-everything-valid option
OR-style mode entries
invalid-combination filtering
current and legacy mode mapping
installed Hashcat mode support check
manual -m override with warning
mode preview
saved mode set metadata
```

Required beginner option:

```text
Try Every Valid VeraCrypt / TrueCrypt Mode
```

Acceptance tests:

```text
TrueCrypt cannot use VeraCrypt-only PRFs or ciphers.
VeraCrypt-only options are not generated for TrueCrypt jobs.
Normal and hidden non-system headers use non-system modes.
System headers use system / boot modes.
Duplicate generated modes are removed.
Unsupported installed-Hashcat modes are shown as skipped, not silently hidden.
Manual override still uses workspace-local input only.
```

## Phase 9: PIM Builder

Goal:

```text
Create VeraCrypt PIM sets.
```

Codex should build:

```text
PIM builder screen
default PIM option
exact PIM input
comma-separated input
newline-separated input
range input
range expansion
deduplication
sorting
preview before save
PIM metadata
PIM list files
job draft update
```

Rules:

```text
PIM applies to VeraCrypt only.
TrueCrypt jobs do not use PIM.
Default PIM is stored as pim_mode: default.
0 is rejected as a custom PIM value.
```

Acceptance tests:

```text
789-805 expands correctly.
Mixed commas and newlines parse correctly.
Duplicates are removed.
Values are sorted ascending.
Invalid values are rejected.
Large lists show warnings.
PIM files stay inside generated/pim-lists/.
```

## Phase 10: Keyfile Builder

Goal:

```text
Import, normalize, and group keyfiles.
```

Codex should build:

```text
no-keyfiles mode
exact selected keyfiles
folder as one keyfile set
folder combination generation
normalized keyfile copies
optional full-copy import
optional workspace-local thumbnails
keyfile metadata
keyfile group metadata
keyfile set metadata
combination preview
dedupe across groups
job draft update
```

Normalization rule:

```text
If keyfile is 1,048,576 bytes or smaller, copy the entire file byte-for-byte.
If keyfile is larger than 1,048,576 bytes, copy only the first 1,048,576 bytes byte-for-byte.
```

Acceptance tests:

```text
Original keyfiles are not modified.
Normalized keyfiles are workspace-local.
Large keyfiles are capped to first 1 MiB.
Small keyfiles are copied exactly.
Keyfile combinations are combinations, not permutations.
Duplicate combinations are removed.
Hashcat job paths never use original keyfile paths by default.
Keyfile contents are not printed in logs.
```

## Phase 11: Password Builder

Goal:

```text
Create password candidate sources.
```

Codex should build:

```text
segment builder
manual password list
imported wordlist copy
external wordlist reference
ordered segments
OR variants per segment
exact text variants
case variants
same characters unknown order
same characters unknown order plus case variants
manual variant lists
pattern token expansion
segment filters before generation
candidate count preview
small-list candidate review
generated wordlist storage
password recipe metadata
job draft update
```

Required user-facing pattern token:

```text
?C = any letter, lowercase or uppercase
```

Do not expose `?1` as a normal user-facing token.

Acceptance tests:

```text
Segment order is preserved.
Variant order is preserved.
Final duplicate cleanup preserves first-seen order.
Candidate count preview works.
Large candidate warnings appear.
Generated wordlists stay in generated/wordlists/.
Temporary candidate chunks stay inside workspace.
External wordlists are marked external and non-portable.
System temp folder is not used.
```

## Phase 12: Final Job Expansion and Command Builder

Goal:

```text
Combine hash modes, PIMs, keyfiles, and password sources into runnable queued jobs.
```

This is the bridge between the builders and the queue runner.

Codex should build:

```text
final job expansion screen
job count preview
VeraCrypt and TrueCrypt split counts
Hashcat argument array builder
command preview generator
workspace-local input validation
workspace-local output path creation
queue job creation
command array save
command preview save
```

Each queued job should include:

```text
normalized header or workspace-derived Hashcat input
Hashcat mode
PIM option if VeraCrypt and custom PIM applies
keyfile option if keyfiles apply
password source
session name placeholder
restore path placeholder
potfile path
outfile path
log path
status log path
```

Required command behavior:

```text
Internal command format: argument array.
Human-readable command string: preview/export only.
```

Acceptance tests:

```text
Generated jobs use only workspace-local headers.
Generated jobs use only normalized workspace keyfiles.
Generated jobs use workspace-local potfile, restore, logs, and output paths.
Command arrays are valid lists.
Command previews are not used for execution.
External wordlists are allowed only when explicitly selected and marked.
Queue job count matches preview.
```

## Phase 13: Queue Runner and Resume

Goal:

```text
Run one Hashcat job at a time and preserve resume state.
```

Codex should build:

```text
queue runner
runner lock
start queue
pause now
pause after current job
stop and save
stop and discard
resume
skip selected job
restart selected job
unique session names per run
workspace-local restore files
workspace-local potfile
workspace-local logs
workspace-local output files
status JSON parsing
result classification
crash recovery prompt
```

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

```text
Only one job can run at a time.
Runner lock blocks duplicate runners for one workspace.
Each run attempt gets a unique session name.
Pause Now pauses active process when supported.
Pause After Current does not interrupt active job.
Stop and Save preserves restore data when possible.
Resume uses restore data and user confirmation.
Crash recovery does not auto-start Hashcat.
Cracked target skips remaining pending jobs for same target/header.
Next job does not start until current result is classified and saved.
```

Use fake Hashcat for automated queue tests.

Fake Hashcat should simulate:

```text
--version
--backend-info
running status output
cracked result
exhausted result
failed result
restore behavior
```

## Phase 14: Reports and Cracked-Result Packages

Goal:

```text
Generate useful reports immediately when a job is cracked.
```

Codex should build:

```text
live cracked-result reporting
non-blocking cracked popup
queue row report actions
Reports screen result viewer
per-cracked-job recovery folder
recovered-result.txt
recovered-result.json
recovered-result.md
stats.txt
command-used.txt
how-to-open-this-volume.txt
recovery-package-manifest.json
CSV cracked-results index
JSON report index
redacted reports
report export warning
report regeneration
```

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

```text
Save raw cracked result first.
Never lose a cracked result because report generation failed.
Copy only the successful normalized job header.
Copy only successful normalized keyfiles.
Do not copy unrelated wordlists or candidate lists.
Reports stay inside the workspace by default.
Passwords are hidden by default in the GUI.
```

Acceptance tests:

```text
Cracked job creates minimum report package.
Report generation failure does not erase cracked result.
CSV index updates.
Report index updates.
Recovery folder contains only successful-job materials.
Password reveal is user-controlled.
Redacted report removes selected sensitive fields.
External export warns and records cleanup manifest entry.
```

## Phase 15: Diagnostic Bundle Export

Goal:

```text
Add a safe support bundle before v1.0.0 so non-technical users can report issues without sharing secrets.
```

Codex should build:

```text
Help → Export Diagnostic Bundle
diagnostic bundle preview
redaction-by-default
sanitized app logs
sanitized error logs
workspace summary
app version
OS version
workspace schema version
Hashcat version if configured
device summary if scanned
missing-path summary
settings summary without sensitive strategy data
```

Diagnostic bundle must exclude by default:

```text
passwords
cracked results
headers
keyfiles
potfiles
generated wordlists
generated candidate chunks
Hashcat output containing recovered secrets
private notes unless the user explicitly includes them
original volumes
```

Suggested diagnostic output folder:

```text
reports/diagnostics/
```

Suggested filename:

```text
diagnostic_bundle_<timestamp>.zip
```

The bundle should stay inside the workspace by default.

If exported outside the workspace, show the external-location cleanup warning and record it in the cleanup manifest.

Acceptance tests:

```text
Diagnostic bundle is redacted by default.
No headers are included.
No keyfiles are included.
No cracked result files are included.
No potfiles are included.
No generated wordlists are included.
Sanitized logs are included.
External export is warned and recorded.
```

## Phase 16: Packaging and Release Zips

Goal:

```text
Create portable release folders for Windows and Linux.
```

Version 1 should not bundle Hashcat by default.

Packaging tool:

```text
PyInstaller
```

Windows package style:

```text
PyInstaller one-folder build
```

Linux package style:

```text
Plain zip only
```

Release zips should include:

```text
Portable app executable or launcher
Required packaged app files
App files
docs/
config/
logs/
tools/hashcat/README-place-hashcat-here.txt
workspaces/default/
```

Windows release example:

```text
PCR-Windows-x64-v0.1.0.zip
```

Linux release example:

```text
PCR-Linux-x64-v0.1.0.zip
```

Suggested portable release folder:

```text
PCR/
  app/
    PCR.exe or launcher
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

Packaging rules:

```text
Do not include sample passwords.
Do not include sample cracked results.
Do not include real headers.
Do not include real keyfiles.
Do not include real potfiles.
Do not include real user workspaces.
Do not include Hashcat unless a later release explicitly adds verified bundling.
Do not write user data into the app folder outside the chosen workspace.
```

Release verification for now:

```text
checksums only
```

Suggested checksum file:

```text
checksums.txt
```

Acceptance tests:

```text
Windows zip extracts and launches on Windows 10 64-bit or newer.
Linux zip extracts and launches on Ubuntu 22.04 LTS or newer.
Default workspace is created.
Hashcat missing warning appears cleanly.
User can browse to Hashcat.
App paths work from a folder with spaces.
App paths work after moving the portable folder.
checksums.txt is generated for release zips.
```

## Phase 17: Windows and Linux Testing

Goal:

```text
Confirm the same workspace rules and basic workflows on both platforms.
```

Minimum supported platforms:

```text
Windows 10 64-bit or newer
Ubuntu 22.04 LTS or newer
glibc 2.35 or newer
```

Windows test checklist:

```text
Launch app from extracted zip.
Create default workspace.
Create custom workspace.
Move portable folder and reopen workspace.
Browse to hashcat.exe.
Verify fake or real Hashcat with --version.
Scan devices.
Extract test header from sample file.
Import a 512-byte header.
Reject oversized imported header.
Create hash mode set.
Create PIM set.
Import normalized keyfile.
Generate small password wordlist.
Create queued job with fake Hashcat.
Run fake cracked job.
Generate report package.
Export redacted diagnostic bundle.
Close and reopen app.
Confirm saved state loads.
```

Linux test checklist:

```text
Launch app from extracted zip or launcher.
Check executable permissions.
Create default workspace.
Create custom workspace.
Browse to hashcat or hashcat.bin.
Verify fake or real Hashcat with --version.
Scan devices.
Test paths with spaces.
Test case-sensitive paths.
Run same fake queue tests.
Export redacted diagnostic bundle.
Confirm no recovery project data is written to /tmp.
```

Shared test rules:

```text
Use fake Hashcat for automated tests.
Use real Hashcat only for optional manual integration testing.
Do not include real encrypted user data in test fixtures.
Use dummy files for header-size and file-handling tests.
```

## Phase 18: Non-Technical User Testing and Issue Reporting

Goal:

```text
Make it easy for a non-technical user to download, test, and report problems.
```

The GitHub release page should include simple steps:

```text
1. Download the Windows or Linux zip.
2. Extract the zip to a normal folder.
3. Open the app launcher.
4. Choose the default workspace or create one.
5. Open Settings → Hashcat Setup.
6. Place Hashcat in tools/hashcat or browse to an existing Hashcat executable.
7. Click Check Hashcat.
8. Add a volume only if you own it or are authorized to recover it.
9. Extract headers into the workspace.
10. Build a job.
11. Run the queue.
12. Open Reports if something is cracked.
```

The app should include:

```text
Help → Open User Guide
Help → Open Workspace Folder
Help → Open Logs Folder
Help → Export Diagnostic Bundle
Help → Report Issue on GitHub
```

GitHub issue templates:

```text
Bug report
Packaging problem
Hashcat setup problem
Queue/resume problem
Report generation problem
Feature request
```

Bug report template should ask for:

```text
App version
Operating system
Release zip used
Hashcat version
What the user was doing
Expected result
Actual result
Screenshot if safe
Sanitized diagnostic bundle
Whether the issue happens again after restart
```

The issue template should warn:

```text
Do not upload passwords, cracked results, headers, keyfiles, potfiles, private wordlists, generated candidate lists, or original volumes.
```

## GitHub Actions / CI

Use GitHub Actions for basic automated checks.

Suggested workflows:

```text
test.yml
lint.yml
build-windows.yml
build-linux.yml
release.yml
```

Minimum CI checks:

```text
Python unit tests
Backend integration tests with fake Hashcat
Path safety tests
Schema load/save tests
Command-array tests
Password builder count tests
PIM parser tests
Keyfile normalization tests
Report generation tests
Diagnostic bundle redaction tests
```

CI should not require:

```text
real GPU
real Hashcat
real VeraCrypt volume
real TrueCrypt volume
real user data
```

## Testing Strategy

Use four test levels.

### Unit Tests

Test small backend functions.

Examples:

```text
PIM parser
password candidate counter
keyfile normalization
hash mode mapping
workspace path safety
atomic writes
cleanup manifest entries
command array construction
diagnostic redaction
```

### Integration Tests

Test combined systems with fake files and fake Hashcat.

Examples:

```text
create workspace
add dummy target
extract dummy header
build job
run fake Hashcat
classify cracked result
generate reports
export redacted diagnostic bundle
resume fake stopped job
```

### Manual Smoke Tests

Run the packaged app like a normal user.

Examples:

```text
open app
create workspace
configure Hashcat
add target
create small test job
run fake queue
view report
export diagnostic bundle
close and reopen
```

### Optional Real Hashcat Tests

Use real Hashcat only for controlled local testing.

Rules:

```text
Do not use unauthorized data.
Do not include real test secrets in the repository.
Do not require real Hashcat in CI.
```

## Release Version Plan

Suggested early version stages:

```text
v0.1.0 - App shell, workspace, settings, logs
v0.2.0 - Hashcat setup and device scan
v0.3.0 - Target wizard and header extraction
v0.4.0 - Hash mode, PIM, keyfile, and password builders
v0.5.0 - Final job expansion and command previews
v0.6.0 - Queue runner with fake Hashcat testing
v0.7.0 - Real Hashcat runner and resume support
v0.8.0 - Reports and recovery folders
v0.9.0 - Diagnostic bundle, Windows/Linux packaged beta
v1.0.0 - First stable release
```

Do not call the app stable until:

```text
workspace save/load is reliable
queue resume is reliable
path safety tests pass
reports do not lose cracked results
diagnostic export is redacted by default
Windows and Linux packages launch cleanly
non-technical setup instructions are written
```

## User Inputs

This build-plan step expects project-maintainer inputs, not app-user inputs.

Maintainer inputs already decided:

```text
license choice
GUI toolkit
packaging tool
Linux release format
Windows packaging format
minimum Python version
minimum Windows version
minimum Linux target
release checksum approach
diagnostic bundle timing
```

Current decisions:

```text
Repository name: portable-crypt-recovery
App name: Portable VeraCrypt/TrueCrypt Recovery GUI
License: MIT License
GUI toolkit: PySide6
Packaging: PyInstaller
Windows package: one-folder
Linux package: plain zip
Minimum Python: 3.12
Minimum Windows: Windows 10 64-bit
Minimum Linux: Ubuntu 22.04 LTS / glibc 2.35
Release verification: checksums only for now
Diagnostic bundle: before v1.0.0, redacted by default
Hashcat bundled: no
Hashcat auto-download: no
John the Ripper: not required
```

## App Behavior

The final built app should:

```text
run locally
support Windows and Linux
use a portable workspace by default
keep app-created sensitive files inside the workspace
avoid system temp folders for recovery project data
use Hashcat as the required backend
not crack passwords itself
build Hashcat commands as argument arrays
run one Hashcat job at a time
save every 60 seconds
save immediately after major changes
resume from saved workspace state after interruption
extract and process only workspace headers
normalize keyfiles into the workspace
generate password lists inside the workspace
generate live cracked-result reports
export redacted diagnostic bundles before v1.0.0
package releases as portable zip folders
```

## Files Created or Modified

This step affects project repository files, not workspace recovery files.

Repository files:

```text
README.md
LICENSE
CHANGELOG.md
SECURITY.md
CONTRIBUTING.md
pyproject.toml
requirements.txt
requirements-dev.txt
.gitignore

docs/project-sources/*
docs/user-guide/*
docs/developer/*

src/portable_crypt_recovery/*
tests/*
scripts/*
packaging/*
.github/workflows/*
.github/ISSUE_TEMPLATE/*
```

Release files:

```text
PCR-Windows-x64-v<version>.zip
PCR-Linux-x64-v<version>.zip
checksums.txt
release-notes.md
```

The running app will create workspace files according to earlier source files.

## Workspace Folders Used

This step does not add new workspace folders.

The build must preserve the workspace layout already decided:

```text
targets/
headers/
jobs/
queue/
hashcat/
inputs/
generated/
temp/
reports/
logs/
cleanup/
```

Packaging should include a default workspace folder:

```text
workspaces/default/
```

The default workspace must be created or repaired on startup if missing.

## Safety Rules

The build plan must preserve all earlier safety rules:

```text
Only support legitimate recovery of user-owned or authorized volumes.
Do not modify original VeraCrypt or TrueCrypt volumes.
Open targets read-only.
Never run Hashcat against original full volumes.
Use normalized 512-byte workspace headers for jobs.
Keep sensitive app-created data inside the workspace by default.
Do not use system temp folders for recovery project data.
Do not silently upload, transmit, or exfiltrate anything.
Do not claim secure deletion is guaranteed.
Describe cleanup as trace centralization and minimization.
Use Hashcat as a local backend only.
Use argument arrays internally.
Do not rely on unsafe shell command strings.
Hide recovered passwords by default in the GUI.
Warn before exporting sensitive files outside the workspace.
Record external exports in the cleanup manifest.
```

GitHub safety rules:

```text
Do not commit real headers.
Do not commit real keyfiles.
Do not commit real cracked results.
Do not commit real potfiles.
Do not commit private wordlists.
Do not commit generated candidate lists.
Do not commit user workspaces.
Do not include test data that can open a real private volume.
```

Recommended `.gitignore` entries:

```text
workspaces/
*.potfile
*.restore
reports/cracked/
generated/wordlists/
generated/candidates/
inputs/keyfiles/
headers/extracted/
headers/normalized/
hashcat/output/
hashcat/logs/
*.log
diagnostic_bundle_*.zip
```

## Open Questions

Open implementation questions:

```text
Exact final app display name.
Exact final repository name if different from portable-crypt-recovery.
Whether Linux zip should later be joined by AppImage after v1.0.0.
Whether release checksums should later become signed checksums.
Whether Hashcat auto-download should be reconsidered after version 1.
Whether optional John the Ripper support should be added after the first stable release.
Exact user guide wording and screenshots.
Exact issue template wording.
```

None of these open questions should block starting Phase 1.

## Final Decisions

```text
Step 11 is the GitHub/Codex build plan.
Earlier source files are decided and should not be redesigned.
Codex should build in phases, not all at once.
Each phase should build on the previous phase.
Each phase should be tested before moving forward.
Backend logic should be separated from GUI code.
The repository should include source files, user docs, developer docs, tests, scripts, and packaging files.
The app should use Python 3.12 and PySide6.
The project license should be MIT License.
Packaging should use PyInstaller.
Windows should use a PyInstaller one-folder portable build.
Linux should ship as a plain zip.
Windows minimum target should be Windows 10 64-bit.
Linux minimum target should be Ubuntu 22.04 LTS or newer, glibc 2.35 or newer.
Release zips should include checksums only for now.
Diagnostic bundle export should be added before v1.0.0 and redacted by default.
Hashcat remains the required backend.
John the Ripper remains optional later.
Version 1 should not auto-download Hashcat.
Release zips should be portable folders for Windows and Linux.
Hashcat should not be bundled by default in version 1.
The release should include a tools/hashcat folder with instructions for the user to place or locate Hashcat.
The app should support non-technical users with simple setup instructions and issue templates.
Automated tests should use fake Hashcat.
Real Hashcat tests should be optional and local.
The app must preserve all workspace, safety, reporting, and cleanup rules from earlier source files.
```
