# 02-workspace-and-portability.md

## Purpose

This step defines the portable folder layout and workspace rules for the Portable VeraCrypt/TrueCrypt Recovery GUI project.

The app should be portable by default and should keep all app-created project data inside one chosen workspace folder unless the user deliberately chooses an external location.

The workspace is where the app stores:

- workspace configuration
- target metadata
- extracted headers
- normalized job headers
- jobs
- queue state
- generated commands and command argument arrays
- command previews and exports
- PIM choices and PIM metadata
- password builder settings
- wordlist build recipes
- generated wordlists
- generated masks
- generated candidates
- keyfile lists
- imported keyfiles by default
- imported wordlists by default
- logs
- Hashcat restore files
- Hashcat potfile
- Hashcat output files
- temporary working files
- cleanup manifest
- reports

A core design goal is one-folder cleanup.

The app should centralize app-created project files into one workspace folder so cleanup is easier at the end of a recovery project. If the user uses a secure deletion tool, they should be able to point it at the workspace folder instead of hunting for files across the system.

The app must not claim that deleting the workspace guarantees secure deletion. The correct wording is:

```text
The app centralizes app-created project files into one folder to make cleanup easier. Secure deletion depends on the user’s filesystem and deletion tool.
```

## Core Workspace Rule

The app uses one chosen workspace folder for each recovery project.

By default, the workspace is inside the portable app folder.

The user may choose a different workspace location.

By default, all app-created sensitive files, semi-sensitive files, and forensic-trail files should stay inside the chosen workspace.

This includes files that are not passwords themselves but could reveal clues about what was being attempted.

Examples include:

- generated commands
- saved Hashcat argument arrays
- command previews
- queue history
- job history
- PIM values or PIM ranges
- mask patterns
- wordlist build recipes
- candidate generation settings
- keyfile list files
- generated password lists
- generated candidate chunks
- Hashcat logs
- app logs
- reports
- restore files
- potfiles
- output files
- temporary staging files

The app must not use the system temp folder for sensitive recovery data or forensic-trail data.

The app must not use the system temp folder for:

- passwords
- password candidates
- keyfiles
- keyfile lists
- headers
- normalized job headers
- Hashcat job files
- PIM data
- generated commands
- generated command previews
- generated wordlists
- generated masks
- generated candidates
- restore files
- potfiles
- cracked-result files
- reports
- any app-created data that can reveal what may be needed to open the volume

## One-Folder Cleanup Goal

The default design should make cleanup simple.

At the end of a project, the user should be able to identify one workspace folder that contains the project’s app-created recovery data.

The app should not scatter project files across multiple locations by default.

This matters because recovery material can reveal patterns about the user’s passwords, PINs, personal history, accounts, or reused credentials.

Even if a file is not directly sensitive, it may still be a clue.

Examples of clue-producing files include:

- mask patterns
- PIM ranges
- rule selections
- wordlist source notes
- generated candidate lists
- job names
- command history
- queue history
- reports
- logs

The app should describe this as trace centralization and minimization, not guaranteed secure deletion.

## External Location Rule

Saving outside the workspace should be allowed only when the user deliberately chooses it.

External locations are an advanced exception, not the default.

When the user chooses an external save location, the app should show a warning:

```text
This file will be saved outside the workspace. At cleanup time, you must remember to delete or securely erase this external location separately. The workspace cleanup process cannot remove files saved elsewhere.
```

The app should mark external files as external and non-portable.

The app should record external paths in the cleanup manifest so the user can see what must be cleaned separately.

The app should avoid copying sensitive data outside the workspace unless the user explicitly chooses that location.

## Cleanup Manifest

The workspace should include a cleanup manifest.

Suggested path:

```text
cleanup/cleanup-manifest.json
```

The cleanup manifest should record app-created files and user-selected external locations.

Suggested contents:

- file ID
- file type
- workspace-relative path, if inside workspace
- absolute path, if external
- whether the file is inside or outside the workspace
- creation timestamp
- last modified timestamp
- owning target ID, if applicable
- owning job ID, if applicable
- cleanup category
- sensitivity category
- notes

Cleanup categories may include:

```text
header
normalized-header
keyfile-copy
wordlist-copy
generated-wordlist
generated-mask
generated-candidate-list
generated-command
job-config
queue-state
hashcat-restore
hashcat-potfile
hashcat-output
log
report
temporary-file
external-reference
```

The cleanup manifest should help the user understand where app-created or app-referenced project data exists.

The cleanup manifest should not store passwords or cracked secrets directly.

## Portable App Folder Layout

Suggested portable app folder layout:

```text
PCR/
  app/
    PCR executable or launcher
    app files
    Python runtime if bundled later
    GUI libraries if bundled later

  tools/
    hashcat/
      hashcat executable
      Hashcat files
      OpenCL or backend files if bundled with Hashcat

  workspaces/
    default/
      workspace files

  config/
    app-global-settings.json
    recent-workspaces.json

  logs/
    app-startup.log

  docs/
    help files
    safety notes
```

The `workspaces/default/` folder is the default workspace.

The `config/` folder may store non-sensitive global app settings, such as:

- recent workspace paths
- UI preferences
- last opened workspace path
- Hashcat tool path if not stored inside the workspace

The portable app folder should not store passwords, extracted headers, normalized job headers, Hashcat potfiles, Hashcat restore files, generated wordlists, cracked results, or forensic-trail project files outside the workspace.

## Workspace Folder Layout

Suggested workspace layout:

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
      imported/
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

  temp/
    active-job/
    staging/

  reports/
    markdown/
    text/
    json/

  logs/
    app/
    queue/
    errors/

  cleanup/
    cleanup-manifest.json
```

## Main Workspace Files

### workspace.json

Stores basic workspace identity and compatibility data.

Suggested contents:

- workspace name
- workspace ID
- created timestamp
- last opened timestamp
- app version
- workspace schema version
- operating system where created
- notes

### settings.json

Stores workspace-specific settings.

Suggested contents:

- Hashcat path for this workspace if custom
- selected compute devices
- default queue behavior
- default cracked-result behavior
- logging preferences
- report preferences
- cleanup warning preferences
- safety confirmation status

### targets/targets.json

Stores metadata for added targets.

Suggested contents:

- target ID
- display name
- original file path
- target type
- container type, VeraCrypt or TrueCrypt
- ownership confirmation status
- extracted header status
- normalized job header status
- extracted header ID
- normalized job header ID
- cracked status
- notes
- timestamps

The original volume file should not be copied into the workspace by default.

The app should only store the original target path and metadata.

### headers/metadata/

Stores metadata about extracted, imported, and normalized headers.

Suggested contents:

- header ID
- target ID
- source type: app-created extraction or user import
- imported header filename, if applicable
- normalized job header filename
- original target path, if applicable
- extraction or import timestamp
- source header size
- normalized header size
- checksum of source header
- checksum of normalized header
- validation status
- notes

### queue/queue-state.json

Stores queue state needed for resume.

Suggested contents:

- queue order
- current running job
- paused job
- stopped job
- completed jobs
- failed jobs
- skipped jobs
- Hashcat session names
- timestamps
- stop behavior
- resume behavior

### hashcat/potfile/

Stores the workspace-specific Hashcat potfile.

The app should configure Hashcat to use a potfile inside the workspace, not the user’s global Hashcat potfile.

### hashcat/restore/

Stores Hashcat restore files for workspace jobs.

Each job should use a unique Hashcat session name so restore files do not conflict.

### hashcat/output/

Stores cracked output files and Hashcat result files.

### jobs/command-arrays/

Stores the saved Hashcat argument arrays used by jobs.

These files may reveal target type, hash mode, PIM choices, wordlist choices, mask choices, rule choices, and other recovery strategy details.

They should be treated as forensic-trail files and kept inside the workspace by default.

### jobs/command-previews/

Stores user-visible command previews and exported command text.

These files should stay inside the workspace by default.

### generated/recipes/

Stores app-created recipes for generated lists, masks, and candidates.

Recipes may reveal personal information patterns or recovery strategy clues, so they should stay inside the workspace by default.

### generated/pim-lists/

Stores generated PIM lists or PIM range files if needed by later steps.

PIM data may reveal recovery strategy and should stay inside the workspace by default.

### logs/

Stores app logs, queue logs, Hashcat logs, errors, and warnings.

Clearing the visible GUI log should not delete saved log files unless the user explicitly chooses to delete them.

Logs should avoid printing secrets directly.

Logs may still reveal project strategy and should stay inside the workspace by default.

### temp/

Stores temporary working files.

The app should clean old temporary files when safe, but should not promise secure deletion.

Temporary files should stay inside the workspace.

### cleanup/

Stores cleanup tracking information.

The cleanup manifest should help the user identify which files are inside the workspace and which user-selected files are outside the workspace.

## Windows Portability

The app should support Windows portable use.

Windows considerations:

- paths may use drive letters
- paths may change when a USB drive is moved
- Hashcat executable may be `hashcat.exe`
- paths may contain spaces
- commands should be built as argument arrays, not raw shell strings
- workspace paths should be stored in a way that supports relocation when possible

The app should prefer relative paths for files inside the workspace.

Absolute paths may be needed for:

- original target files
- external wordlists if the user chooses external reference mode
- custom Hashcat location outside the portable folder
- user-selected external export locations

The app should detect missing paths and show clear repair options.

## Linux Portability

The app should support Linux portable use.

Linux considerations:

- Hashcat executable may be `hashcat`
- file permissions may block execution
- mounted drives may use different paths on different systems
- case-sensitive paths must be respected
- commands should be built as argument arrays, not raw shell strings
- workspace files should avoid Windows-only filename characters where possible

The app should check whether the Hashcat executable has permission to run.

The app should avoid assuming that Linux paths remain stable across machines.

## Cross-Platform Filename Rules

Workspace-created filenames should be safe on Windows and Linux.

Use:

- lowercase letters
- numbers
- hyphens
- underscores
- short IDs

Avoid:

- colons
- question marks
- asterisks
- quotes
- angle brackets
- pipe characters
- trailing spaces
- very long filenames

Suggested generated file pattern:

```text
target_<id>_source_header.bin
target_<id>_job_header_512.bin
job_<id>.json
job_<id>.log
session_<id>
report_<id>.md
```

## Path Storage Rules

The app should store workspace-internal paths as relative paths when possible.

Example:

```text
headers/normalized/target_001_job_header_512.bin
hashcat/logs/job_001.log
generated/wordlists/job_001_candidates.txt
```

The app may store absolute paths for files outside the workspace.

External absolute paths should be marked as external and non-portable.

If an external path is missing, the app should ask the user to locate the file again.

External paths should also be recorded in the cleanup manifest.

## Import Options

## Target Import

Targets are original VeraCrypt or TrueCrypt volumes.

Target import means adding the target path and metadata to the workspace.

The app should:

- browse for a target file or device path
- open the target read-only
- require ownership or authorization confirmation
- store target metadata in the workspace
- extract the header into the workspace
- normalize the needed 512-byte job header inside the workspace
- never modify the original target
- never run Hashcat directly against the original target

The app should not copy full target volumes into the workspace by default.

Hashcat jobs should only use normalized 512-byte job headers stored inside the workspace.

## Header Import

The user may import an already extracted header file.

Header handling should use these rules:

```text
If app-created: require exactly 512 bytes.
If user-imported: allow up to 128 KiB, then normalize/extract the needed 512-byte job header inside the workspace.
Reject files larger than 128 KiB.
```

App-created headers used for jobs must be exactly 512 bytes.

User-imported header files may be larger because they may contain more data than the exact Hashcat job header.

For user-imported headers, the app should:

- copy the imported header into `headers/imported/`
- reject the file if it is larger than 128 KiB
- extract or normalize the needed 512-byte job header into `headers/normalized/`
- store metadata in `headers/metadata/`
- use only the normalized 512-byte job header for Hashcat jobs

Files larger than 128 KiB should be rejected as likely wrong input for this workflow.

The exact VeraCrypt and TrueCrypt extraction behavior is handled in Step 5.

## Keyfile Import

Keyfiles may be sensitive.

Default behavior:

- copy selected keyfiles into `inputs/keyfiles/imported/`
- use the workspace copy for jobs
- store keyfile metadata in `inputs/keyfiles/manifests/`
- never modify the original keyfile
- avoid storing keyfile contents anywhere except the copied keyfile itself

The app should not use system temp folders for keyfiles.

For portability and trace minimization, Hashcat jobs should use workspace-local keyfile copies by default.

The app may store metadata such as:

- keyfile ID
- imported filename
- workspace path
- size
- checksum
- import timestamp

The app should not print keyfile contents in logs or reports.

## Wordlist Import

Wordlists may be imported in two ways.

Default mode:

```text
Copy into workspace
```

This copies the wordlist into:

```text
inputs/wordlists/imported/
```

This is the most portable and cleanup-friendly option.

Optional mode:

```text
Reference external wordlist
```

This keeps the wordlist outside the workspace and stores only the path.

External reference mode is useful for very large wordlists, but it is less portable and harder to clean up.

External wordlists should be clearly marked as external.

If the external wordlist is missing later, the app should show a repair prompt.

If the user chooses an external wordlist, the app should show a cleanup warning and record the path in the cleanup manifest.

Generated wordlists must always be written inside:

```text
generated/wordlists/
```

The app should not generate password candidates in system temp folders.

## Rules and Mask Import

Imported Hashcat rule files should go in:

```text
inputs/rules/imported/
```

Imported mask files should go in:

```text
inputs/masks/imported/
```

Generated masks should go in:

```text
generated/masks/
```

The app should keep imported and generated files separate.

Masks can reveal password strategy and should be treated as forensic-trail files.

## PIM Data

PIM settings, PIM ranges, and generated PIM lists should stay inside the workspace by default.

Suggested folders:

```text
generated/pim-lists/
generated/recipes/
```

PIM data may not be a password, but it can help recover a VeraCrypt volume and should be treated as sensitive project data.

## Generated Commands

Generated commands and saved Hashcat argument arrays should stay inside the workspace by default.

Suggested folders:

```text
jobs/command-arrays/
jobs/command-previews/
generated/commands/
```

The app should treat generated commands as forensic-trail files because they reveal:

- hash mode
- target type
- input header path
- wordlist or mask choices
- rule choices
- keyfile usage
- PIM settings or ranges
- output locations
- restore settings

The app should not save generated command previews outside the workspace unless the user explicitly chooses to export them elsewhere.

If the user exports a command outside the workspace, the app should warn that the exported command must be cleaned separately.

## Temporary Files

Temporary files should be stored inside:

```text
temp/
```

Suggested use:

```text
temp/active-job/
temp/staging/
```

The app should use this folder for:

- staged imports
- generated candidate chunks
- temporary keyfile lists
- temporary job files
- temporary command preview exports
- temporary PIM lists
- temporary generated recipes

The app must never use the operating system temp folder for sensitive job data or forensic-trail project data.

The app may clean temporary files after a job finishes, but should not claim secure deletion.

## Hashcat Workspace Integration

Hashcat should be configured so job-related files stay inside the workspace.

Hashcat job files should use workspace paths for:

- normalized 512-byte job header input
- keyfiles
- generated wordlists
- generated masks
- generated candidates
- restore files
- potfile
- logs
- output files

Hashcat should not use the default global potfile location.

Hashcat should not use restore files outside the workspace.

Each job should have:

- unique job ID
- unique Hashcat session name
- job log file
- output file
- restore file location
- saved command argument array
- command preview file if the user chooses to save one

## Autosave and Resume Storage

The workspace should support resume after app restart, crash, or interruption.

Autosave files should be stored in:

```text
queue/autosaves/
```

Autosave behavior:

- save every 60 seconds
- save immediately after major changes
- save before starting a Hashcat job
- save after pausing
- save after stopping
- save after job completion
- save after cracked result detection
- save after imports
- save after command generation
- save after external location selection

Autosave files should not be stored outside the workspace.

## Recent Workspaces

Recent workspace paths may be stored in the portable app `config/` folder.

Recent workspace data should contain only:

- workspace path
- display name
- last opened timestamp

Recent workspace data should not contain:

- passwords
- candidate lists
- keyfile contents
- extracted headers
- normalized headers
- potfile data
- cracked results
- Hashcat output
- generated commands
- PIM data
- wordlist recipes
- mask patterns
- recovery strategy details

## Setup Warning

During workspace setup, the app should explain the cleanup tradeoff clearly.

Suggested wording:

```text
By default, this app stores app-created project files inside one workspace folder. This makes cleanup easier at the end of the project.

If you save files outside the workspace, you must remember to clean those locations separately. External files may include logs, generated lists, command exports, reports, or other files that reveal recovery strategy.

The app centralizes app-created project files into one folder to make cleanup easier. Secure deletion depends on your filesystem and deletion tool.
```

## Safety Rules

The app must follow these rules:

- only support legitimate recovery of user-owned volumes
- require user confirmation that they own or are authorized to recover the target
- never modify original VeraCrypt or TrueCrypt volumes
- open original targets read-only
- never run Hashcat directly against original volumes
- only run Hashcat against normalized 512-byte job headers inside the workspace
- require app-created job headers to be exactly 512 bytes
- allow user-imported headers up to 128 KiB
- normalize user-imported headers into 512-byte job headers inside the workspace
- reject imported header files larger than 128 KiB
- keep sensitive generated files inside the workspace by default
- keep forensic-trail project files inside the workspace by default
- treat external save locations as advanced exceptions
- warn users when saving outside the workspace
- record external save locations in the cleanup manifest
- do not use system temp folders for password, keyfile, header, PIM, command, candidate, Hashcat job, or forensic-trail data
- do not silently upload, transmit, or exfiltrate anything
- do not claim secure deletion is guaranteed
- describe cleanup as trace centralization and minimization, not guaranteed secure deletion

## Files Created or Modified

This step defines these workspace-created or workspace-modified files:

```text
workspace.json
settings.json
targets/targets.json
targets/target-notes/*
targets/imported-target-metadata/*
headers/imported/*
headers/normalized/*
headers/extracted/*
headers/metadata/*
jobs/drafts/*
jobs/queued/*
jobs/completed/*
jobs/failed/*
jobs/skipped/*
jobs/command-arrays/*
jobs/command-previews/*
queue/queue-state.json
queue/autosaves/*
queue/history/*
hashcat/sessions/*
hashcat/restore/*
hashcat/potfile/*
hashcat/logs/*
hashcat/output/*
inputs/keyfiles/imported/*
inputs/keyfiles/manifests/*
inputs/wordlists/imported/*
inputs/wordlists/manifests/*
inputs/rules/imported/*
inputs/masks/imported/*
generated/wordlists/*
generated/masks/*
generated/candidates/*
generated/keyfile-lists/*
generated/pim-lists/*
generated/recipes/*
generated/commands/*
temp/active-job/*
temp/staging/*
reports/markdown/*
reports/text/*
reports/json/*
logs/app/*
logs/queue/*
logs/errors/*
cleanup/cleanup-manifest.json
```

The portable app folder may also create or modify:

```text
config/app-global-settings.json
config/recent-workspaces.json
logs/app-startup.log
```

These portable app config files must not contain sensitive recovery data or recovery strategy details.

## Workspace Folders Used

The main workspace folders are:

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

The app should create missing workspace folders when opening or creating a workspace.

The app should validate the workspace structure on startup.

If folders are missing, the app may repair them after user confirmation or automatically if no data loss is possible.

## App Behavior

The app should:

- create a default workspace inside the portable app folder
- allow the user to choose a different workspace
- store app-created recovery data inside the workspace by default
- store forensic-trail project data inside the workspace by default
- make one-folder cleanup a core design goal
- store workspace-internal paths as relative paths where possible
- mark external paths clearly
- record external paths in the cleanup manifest
- warn users when saving outside the workspace
- keep keyfiles workspace-local for jobs by default
- copy imported headers into the workspace
- normalize imported headers into 512-byte job headers inside the workspace
- copy imported wordlists by default
- allow external wordlist references as an optional non-portable mode
- store generated commands inside the workspace
- store PIM data inside the workspace
- store Hashcat restore files inside the workspace
- store Hashcat potfile inside the workspace
- store Hashcat logs inside the workspace
- store Hashcat output inside the workspace
- store reports inside the workspace
- store temporary sensitive files inside the workspace
- store temporary forensic-trail files inside the workspace
- avoid system temp folders for sensitive job data
- avoid system temp folders for forensic-trail project data
- warn when workspace portability or cleanup simplicity is reduced by external references
- detect missing external paths and provide repair options

## Open Questions

Open questions for later steps:

- exact Hashcat command arguments for workspace-local restore files, potfile, logs, and output
- exact VeraCrypt and TrueCrypt header extraction method
- exact method for normalizing imported headers into 512-byte job headers
- exact metadata schema for targets and headers
- exact queue state schema
- exact report formats
- exact cleanup manifest schema
- exact cleanup screen behavior
- exact handling of device or partition targets
- exact behavior for very large external wordlists
- exact UI wording for portability and cleanup warnings

## Final Decisions

- The app uses one chosen workspace folder for each recovery project.
- The default workspace is inside the portable app folder.
- The user may choose a different workspace location.
- One-folder cleanup is a core design goal.
- The app should centralize app-created project files into one workspace folder by default.
- The app must not claim that deleting the workspace guarantees secure deletion.
- The app should say that secure deletion depends on the user’s filesystem and deletion tool.
- Generated sensitive files must stay inside the workspace by default.
- Forensic-trail project files must stay inside the workspace by default.
- Generated commands must stay inside the workspace by default.
- Saved Hashcat argument arrays must stay inside the workspace by default.
- PIM data must stay inside the workspace by default.
- Wordlist build recipes must stay inside the workspace by default.
- Generated masks and candidate files must stay inside the workspace by default.
- The app must not use system temp folders for sensitive project data.
- The app must not use system temp folders for forensic-trail project data.
- External save locations are advanced exceptions, not the default.
- The app should warn users when they save outside the workspace.
- The app should record external paths in a cleanup manifest.
- Workspace-internal paths should be stored as relative paths where possible.
- External paths should be clearly marked as external and non-portable.
- Original target volumes should not be copied into the workspace by default.
- Original target volumes must be opened read-only.
- Hashcat jobs must use normalized 512-byte job headers only.
- App-created job headers must be exactly 512 bytes.
- User-imported headers may be up to 128 KiB.
- User-imported headers must be normalized into 512-byte job headers inside the workspace.
- Imported header files larger than 128 KiB must be rejected.
- Keyfiles should be copied into the workspace for job use by default.
- Wordlists should be copied into the workspace by default.
- External wordlist reference mode may be allowed for very large wordlists, but it should be clearly marked as non-portable and harder to clean up.
- Generated wordlists, masks, candidates, PIM lists, command files, and keyfile lists must be stored inside the workspace.
- Hashcat restore files must be stored inside the workspace.
- Hashcat potfile must be stored inside the workspace.
- Hashcat logs and output files must be stored inside the workspace.
- Reports must be stored inside the workspace.
- Recent workspace paths may be stored outside the workspace only if they contain no sensitive recovery data or recovery strategy details.
