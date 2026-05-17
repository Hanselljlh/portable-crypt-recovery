# 01-basic-program-workings.md

## Purpose

The app is a local desktop GUI for legitimate recovery of user-owned VeraCrypt and TrueCrypt volumes.

The app does not crack passwords itself. Hashcat is the required backend. The app prepares, organizes, previews, saves, and later runs Hashcat jobs.

The first version should stay simple:

- local GUI only
- Windows and Linux support
- portable by default
- one chosen workspace
- one queue
- one Hashcat job running at a time
- saved state and resume support
- sensitive generated files kept inside the workspace
- original volumes never processed directly by Hashcat
- Hashcat jobs process extracted headers only

## Basic App Workflow

The basic workflow is:

```text
Start app
→ Use default workspace, browse for workspace, or select recent workspace
→ Add VeraCrypt or TrueCrypt target
→ Confirm ownership and safety rules
→ Extract header into workspace
→ Prepare recovery job using extracted header
→ Add job to queue
→ Run job with Hashcat later
→ Save logs, restore files, results, and reports
```

## Startup Flow

On startup, the app should show a simple workspace selection screen.

The app should start with a default workspace folder inside the portable app structure. The user may use that default folder or choose a different workspace location.

Startup choices:

```text
Use Default Portable Workspace
Browse for Saved Workspace
Recent Workspaces
```

### Use Default Portable Workspace

The app uses the default workspace folder inside the portable app structure.

If the workspace does not exist yet, the app creates it.

If the workspace already exists, the app opens it and loads saved state.

### Browse for Saved Workspace

The user selects an existing workspace folder or chooses a new workspace location.

The app checks for the workspace configuration file.

If the folder contains a valid workspace, the app loads saved targets, jobs, settings, logs, and results.

If the folder is empty or not yet configured, the app may offer to create a new workspace there.

### Recent Workspaces

The app may show a list of recently opened workspaces.

Recent workspace paths may be saved outside the workspace, but sensitive recovery data should not be saved there.

There should not be separate flows for “open existing workspace” and “open recent workspace.” Both are ways to open a saved workspace.

## Main Screens

The app should have these main screens:

```text
Dashboard
Targets
Jobs
Queue
Logs
Reports
Settings
```

## Dashboard

The Dashboard shows the overall project state:

- workspace name and path
- number of targets
- number of extracted headers
- number of queued jobs
- current running job, if any
- cracked or not cracked status
- recent activity
- warnings or missing setup items

Main buttons:

```text
Add Target
Create Job
Open Queue
Open Reports
Settings
```

## Targets Screen

The Targets screen lists added VeraCrypt and TrueCrypt targets.

Each target should show:

- display name
- original file path
- container type: VeraCrypt or TrueCrypt
- target type, such as file container or device/partition if supported later
- header extraction status
- extracted header path
- number of jobs created
- cracked status
- notes

Main buttons:

```text
Add Target
Remove Target
View Target Details
Extract Header
Create Job From Header
```

The app must never modify the original target.

The app must never run Hashcat directly against the original volume.

## Job Builder Screen

The Job Builder screen prepares recovery jobs.

Step 1 only defines the basic flow:

```text
Target
→ Extracted header
→ Recovery options
→ Password source
→ Hashcat settings
→ Queue job
```

Later steps will design:

- hash mode builder
- PIM builder
- keyfile builder
- password builder
- Hashcat command builder

Main buttons:

```text
Save Job
Add to Queue
Preview Command Later
Cancel
```

A job should only be created from an extracted header stored inside the workspace.

## Queue Screen

The Queue screen lists jobs waiting to run.

Each job should show:

- job name
- target
- extracted header used
- status
- progress, if known
- Hashcat session name
- start time
- stop time
- result

Supported statuses:

```text
Draft
Queued
Running
Paused
Stopped
Completed
Cracked
Exhausted
Failed
Skipped
```

Queue controls:

```text
Start Queue
Pause Now
Pause After Current Job
Stop and Save
Stop and Discard
Resume
Skip Job
Restart Selected Job
```

The app should run only one Hashcat job at a time.

Pause Now is required because a current job may run for hours and the user may need the computer for something else.

Pause After Current Job is also required because the user may want the current job to finish cleanly before stopping the queue.

## Logs Screen

The Logs screen shows app and Hashcat activity.

It should include:

- app events
- queue events
- Hashcat output logs later
- errors
- warnings

Main buttons:

```text
Open Log Folder
Export Log Later
Clear View
```

Clearing the visible log view should not automatically delete saved log files.

## Reports Screen

The Reports screen is reserved for later report generation.

Reports should eventually include:

- target summary
- extracted header summary
- job summary
- cracked result if found
- settings used
- timestamps
- output file locations

## Settings Screen

The Settings screen should include:

- Hashcat location, added later
- workspace location
- default cracked-result behavior
- compute device selection
- interface preferences
- safety confirmation status

Compute device selection should support available devices detected by Hashcat, including:

- NVIDIA GPU
- AMD GPU
- Intel GPU
- CPU
- multiple GPUs
- GPU plus CPU for maximum available speed

The app should allow the user to choose which available devices Hashcat may use.

If multiple devices are available, the user should be able to select one, several, or all of them.

If the user does not need to use the computer while a job runs, they may choose GPU plus CPU for maximum available speed.

Settings must avoid storing sensitive password material outside the workspace.

## Main Controls

The app should have a simple top-level layout.

Suggested left sidebar:

```text
Dashboard
Targets
Jobs
Queue
Logs
Reports
Settings
```

Suggested global controls:

```text
Save
Open Workspace
Close Workspace
Help
Exit
```

Suggested queue controls:

```text
Start
Pause Now
Pause After Current
Stop and Save
Stop and Discard
Resume
Skip
Restart Selected
```

Suggested target controls:

```text
Add Target
Remove Target
Target Details
Extract Header
Create Job From Header
```

Suggested safety controls:

```text
Confirm Ownership
Open Read-Only
Validate Header File
View Safety Notes
```

## Hashcat Connection Design

Hashcat is external and required.

The app should connect to Hashcat through a controlled backend layer.

The GUI should not directly build unsafe shell strings.

Hashcat commands should be stored internally as argument arrays.

Command strings may be shown only for preview or export.

The Hashcat backend should later handle:

- locating Hashcat
- checking Hashcat version
- checking available devices
- presenting NVIDIA, AMD, Intel, and CPU options when available
- building command arguments
- starting the Hashcat process
- pausing jobs now
- pausing after the current job
- reading Hashcat output
- saving logs
- detecting cracked results
- handling restore files
- stopping jobs
- resuming jobs

Exact Hashcat setup is handled in Step 3.

## User Inputs

The basic app should eventually accept these user inputs:

- workspace location
- target VeraCrypt or TrueCrypt volume path
- confirmation that the user owns or is authorized to recover the target
- target display name
- target notes
- extracted header selection or extraction request
- job name
- job settings, defined in later steps
- queue control actions
- compute device choices, defined further in Step 3

## App Behavior

The app should:

- start with a default workspace inside the portable app structure
- let the user browse for a saved workspace
- let the user choose from recent workspaces
- create or load workspace state
- add targets without modifying them
- open original target files read-only
- extract headers into the workspace
- create jobs only from extracted headers
- reject attempts to run Hashcat directly against original volumes
- save workspace state automatically
- run one Hashcat job at a time
- support pause now
- support pause after current job
- support stop and save
- support stop and discard
- support resume
- support skip
- support restart selected job
- track job status and results
- keep logs and generated files inside the workspace

## Saved State

The app should save workspace state.

Minimum saved data:

- workspace configuration
- app version used for workspace
- targets list
- target metadata
- extracted header metadata
- job drafts
- queued jobs
- job statuses
- Hashcat session names
- queue order
- selected compute devices
- logs
- results
- user notes
- safety acknowledgement
- last opened screen
- timestamps

The app should auto-save every 60 seconds.

The app should also save immediately after major changes, including:

- workspace creation
- adding or removing a target
- extracting a header
- creating a job
- adding a job to queue
- starting a queue
- pausing a job
- stopping a job
- completing a job
- finding a cracked password
- changing important settings

## Files Created or Modified

This step does not define the full workspace structure yet. That is handled in Step 2.

At minimum, the app will eventually need to create or modify:

```text
workspace configuration file
targets list file
extracted header files
extracted header metadata file
jobs or queue state file
settings file
app log file
Hashcat log files later
Hashcat restore files later
Hashcat potfile later
result files later
report files later
```

Exact filenames and folders are decided in Step 2.

## Workspace Folders Used

Step 1 only decides that one chosen workspace folder should contain generated project data.

Detailed workspace folder layout is handled in Step 2.

The workspace should eventually contain:

```text
configs
targets metadata
extracted headers
jobs
queues
logs
restore files
potfile
outputs
reports
temporary working files
generated wordlists
```

The default workspace should be inside the portable app structure.

The user may choose a different workspace location.

## Header-Only Processing Rule

The app must never process original volumes directly with Hashcat.

Hashcat jobs must only use extracted header files stored inside the workspace.

The app should include a safety check to reduce the chance that a user accidentally selects a full VeraCrypt or TrueCrypt volume instead of a header file.

The check should reject files that are much larger than expected header size.

The exact size limit should be finalized during the header extraction step, but Step 1 decides the general rule:

- header files should be small
- full volumes are usually much larger
- files larger than 128 MB should be treated as likely full volumes, not headers
- the app should warn and refuse to process oversized files as Hashcat job input

The wording should stay flexible enough for VeraCrypt and TrueCrypt header-size differences.

## Safety Rules

The app must follow these rules:

- only support legitimate recovery of user-owned volumes
- require user confirmation that they are working on their own volume or are authorized to recover it
- never modify original VeraCrypt or TrueCrypt volumes
- open target files read-only
- extract headers into the workspace
- process extracted headers only
- never run Hashcat directly against original volume files
- reject oversized job input files that are likely full volumes
- keep generated files inside the workspace
- do not use system temp folders for password, keyfile, or header data
- do not silently upload, transmit, or exfiltrate anything
- do not claim secure deletion is guaranteed
- explain that the goal is to centralize and minimize traces
- keep Hashcat logs, restore files, potfiles, output files, and reports inside the workspace

## Open Questions

Open questions for later steps:

- exact workspace folder layout
- exact saved file formats
- exact Hashcat setup process
- exact compute device detection and selection behavior
- exact queue resume behavior
- exact pause now behavior for Hashcat processes
- exact header extraction behavior
- exact header file size validation limits
- exact VeraCrypt and TrueCrypt hash mode handling
- exact password builder behavior
- exact report format

## Final Decisions

- The app is a local GUI for legitimate recovery of user-owned VeraCrypt and TrueCrypt volumes.
- The app does not crack passwords itself.
- Hashcat is the required backend.
- The app builds and manages Hashcat jobs.
- The app should run one Hashcat job at a time.
- The app should start with a default workspace inside the portable app structure.
- The user can browse for a saved workspace or choose from recent workspaces.
- Open existing workspace and recent workspace are not separate concepts. Both open saved workspaces.
- The app should be portable by default.
- The app should save automatically every 60 seconds.
- The app should save immediately after major changes.
- The app should support resume after crash, restart, or interruption.
- The queue must support Pause Now.
- The queue must support Pause After Current Job.
- The settings screen must support selectable compute devices.
- Compute device options should include NVIDIA GPU, AMD GPU, Intel GPU, CPU, multiple GPUs, and GPU plus CPU when available.
- The app should never modify original target volumes.
- The app should open target files read-only.
- The app should extract headers into the workspace.
- The app should only create Hashcat jobs from extracted headers.
- The app should never run Hashcat directly against original volumes.
- The app should reject files that are much larger than expected header size.
- Files larger than 128 MB should be treated as likely full volumes, not headers.
- The app should keep generated sensitive files inside the workspace.
- The app should not claim secure deletion is guaranteed.
- Hashcat commands should be stored internally as argument arrays.
- Command strings are only for preview or export.
