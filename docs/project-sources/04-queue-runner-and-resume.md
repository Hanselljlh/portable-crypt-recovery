# 04-queue-runner-and-resume.md

## Purpose

This step defines how the app runs queued Hashcat jobs and resumes after interruption.

The app should run one Hashcat job at a time.

The next job should start only after the current job exits, is classified, and the workspace state is saved.

The queue runner should support:

- start
- pause now
- pause after current job
- stop and save
- stop and discard
- resume
- skip
- restart selected job
- auto-save every 60 seconds
- immediate save after major changes
- crash recovery
- unique Hashcat sessions per job
- workspace-local restore files
- workspace-local potfile
- workspace-local logs
- workspace-local output files

The app still does not crack passwords itself. It starts, monitors, pauses, stops, resumes, and records Hashcat jobs.

## User Inputs

The Queue screen should accept these user actions:

```text
Start Queue
Pause Now
Pause After Current Job
Stop and Save
Stop and Discard
Resume
Skip Selected Job
Restart Selected Job
```

The user should also be able to choose one queue-level behavior for what happens after any target/header is cracked:

```text
Queue behavior after successful crack:
- Continue with other uncracked targets
- Stop entire queue
```

Recommended default:

```text
Continue with other uncracked targets
```

There should not be an option to keep running more jobs against the same target/header after it is cracked.

Once a target/header is cracked, the app should automatically skip remaining pending jobs for that same target/header.

## Queue Screen

The Queue screen should show the ordered job list.

Each job should show:

- job name
- job ID
- target name
- target ID
- container family: VeraCrypt or TrueCrypt
- header type, if known
- normalized header path
- hash mode
- password source
- PIM value or PIM range, if VeraCrypt
- keyfile set, if used
- status
- progress, if known
- current speed, if known
- Hashcat session name
- restore file path
- output file path
- log file path
- start time
- stop time
- result

The screen should make clear that only one job can run at a time.

## Job Statuses

The queue runner should use these main statuses:

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

Additional UI-only or builder statuses may exist, but the runner should keep its own status handling simple.

### pending

The job is in the queue and has not run yet, or it was reset for another run.

### running

The job currently has an active Hashcat process.

Only one job may have this status at a time.

### paused

The active Hashcat process is paused but still running and controlled by the app.

This is for short-term pausing while the app remains open.

### stopped_saved

The Hashcat process was stopped in a way that preserves restore data when possible.

The job may be resumed from its restore file.

### cracked

Hashcat found a password for the job.

The app should save the cracked result, mark the job as cracked, mark the target/header record as cracked, and apply the queue behavior after successful crack.

### exhausted

Hashcat completed the job without finding a password.

### failed

The job could not complete because of an error.

Examples:

- Hashcat crashed
- Hashcat executable missing
- bad command arguments
- missing input file
- missing wordlist
- missing keyfile
- invalid restore file
- driver or runtime error
- app lost control and no reliable restore exists

### skipped

The user skipped the job, or the app skipped the job because its target/header was already cracked by another job.

Skipped jobs should not run unless the user restarts them.

## Completed Jobs

The app may display a general “completed” grouping in the UI, but the saved job result should use a specific final status:

```text
cracked
exhausted
failed
skipped
```

This keeps reports and resume behavior clear.

## Queue Control Behavior

### Start Queue

When the user starts the queue, the app should:

1. Confirm no other job is running.
2. Confirm Hashcat is configured and verified.
3. Confirm the workspace is writable.
4. Confirm queue state can be saved.
5. Confirm required workspace folders exist.
6. Confirm each runnable job uses a normalized workspace header.
7. Confirm the job does not point to an original volume.
8. Confirm required input files exist.
9. Confirm restore, potfile, log, and output paths are inside the workspace.
10. Save queue state before launching Hashcat.
11. Start the first pending job whose target/header is not already cracked.
12. Mark that job as running.
13. Save queue state immediately after launch.

The app should not start the next job until the current job exits and its result is saved.

### Pause Now

Pause Now should pause the active Hashcat process without ending the job.

Expected behavior:

- send Hashcat’s pause command when available
- keep the Hashcat process alive
- mark the job as paused
- save queue state immediately
- keep the queue from starting another job
- allow Resume to continue the same active process

Pause Now is meant for short-term pauses while the app remains open.

If the user needs to close the app, shut down the computer, or move the workspace, they should use Stop and Save instead.

### Pause After Current Job

Pause After Current Job should not interrupt the active job.

Expected behavior:

- set a queue-level flag
- allow the current job to finish
- classify the current job result
- save the result
- do not start the next pending job
- set queue state to paused after current job ends

This is the safest option when the user wants the current job to finish cleanly before the queue stops.

### Stop and Save

Stop and Save should stop the active Hashcat job while preserving restore data when possible.

Expected behavior:

- request Hashcat checkpoint or clean stop when possible
- save Hashcat restore data inside the workspace
- save queue state immediately
- mark the job as stopped_saved if resume data is available
- mark the queue as stopped
- do not start the next job

The app should warn that stopping at a checkpoint may take time.

If the app cannot confirm a valid restore file, it should mark the job as failed or interrupted and offer Restart Selected Job.

### Stop and Discard

Stop and Discard should stop the active job and discard resume progress for the current run.

Expected behavior:

- stop the active Hashcat process
- do not preserve the current run as resumable
- mark the active run attempt as discarded
- return the job to pending, or mark it failed if the stop was abnormal
- archive or mark the old restore file obsolete
- save queue state immediately

Stop and Discard should not delete the job definition.

It should not claim secure deletion.

If files are removed from the workspace, the app should treat that as normal deletion only and update the cleanup manifest.

### Resume

Resume should support two cases.

#### Resume a paused active process

If the app is still open and the Hashcat process is paused:

- send Hashcat’s resume command
- mark the job as running
- save queue state immediately

#### Resume after stop, restart, or crash

If the app was closed, restarted, or crashed:

- load queue state
- detect the last running or stopped_saved job
- check for its restore file
- check its Hashcat session name
- check that the workspace paths still exist
- rebuild the restore command as an argument array
- resume Hashcat from the saved session and restore file
- mark the job as running
- save queue state immediately

The app should not automatically resume cracking after a crash without user action.

On startup, it should show a recovery prompt instead.

Suggested recovery prompt:

```text
A previous Hashcat job appears to have been interrupted.

Job: <job name>
Session: <session name>
Restore file: <path>

Choose:
- Resume from restore
- Restart from beginning
- Skip job
- Leave queue stopped
```

### Skip Selected Job

Skip should mark a selected pending, failed, exhausted, or stopped job as skipped.

If the selected job is currently running, the app should require the user to stop it first.

Skipped jobs should remain visible in the queue history.

Skipped jobs should not be deleted.

### Restart Selected Job

Restart Selected Job should start a job again from the beginning.

Expected behavior:

- keep the same job definition
- create a new run attempt ID
- create a new unique Hashcat session name
- archive or mark old restore data obsolete
- preserve previous logs and results
- set the job status to pending
- save queue state immediately

Restart should be allowed for:

```text
cracked
exhausted
failed
skipped
stopped_saved
```

Restarting a cracked job should require confirmation because it may create duplicate work.

If the job’s target/header is already marked cracked, the app should warn the user:

```text
This target/header is already marked as cracked.
Successful job: <job name>
Cracked result file: <path>

Restarting this job may repeat work.
```

## Queue Ordering

The queue should run jobs in visible order from top to bottom.

The first pending job whose target/header is not already cracked should run first.

Jobs with final statuses should be skipped by the runner unless restarted.

Final statuses:

```text
cracked
exhausted
failed
skipped
```

If the user reorders pending jobs, the app should save immediately.

If a job is running, reordering should not affect the active job.

## One-Job-at-a-Time Rule

The queue runner must enforce one active Hashcat process per workspace.

The app should use a runner lock file inside the workspace.

Suggested path:

```text
queue/runner-lock.json
```

The lock file should record:

- workspace ID
- active job ID
- active run attempt ID
- Hashcat session name
- process ID, if available
- start timestamp
- app instance ID
- last heartbeat timestamp

On startup, the app should check for a runner lock.

If the lock appears stale, the app should show a recovery screen.

If another app instance is actively running the queue, the app should not start another queue process for the same workspace.

## Unique Hashcat Sessions

Each run attempt should have a unique Hashcat session name.

Suggested pattern:

```text
session_<job_id>_<run_id>
```

Example:

```text
session_job_00042_run_00003
```

The app should avoid reusing session names.

Each run attempt should have its own restore file.

Suggested restore path:

```text
hashcat/restore/session_job_00042_run_00003.restore
```

The session name should be saved in:

```text
queue/queue-state.json
jobs/queued/job_<id>.json
hashcat/sessions/session_<id>.json
```

## Required Hashcat Job Paths

Each job run should use workspace-local paths for:

```text
normalized header
restore file
potfile
Hashcat log
status log
output file
```

Suggested paths:

```text
headers/normalized/target_<id>_job_header_512.bin
hashcat/restore/session_<job_id>_<run_id>.restore
hashcat/potfile/workspace.potfile
hashcat/logs/job_<job_id>_run_<run_id>.log
hashcat/logs/job_<job_id>_run_<run_id>_status.jsonl
hashcat/output/job_<job_id>_run_<run_id>_outfile.txt
hashcat/sessions/session_<job_id>_<run_id>.json
```

Hashcat should not use the user’s global potfile.

Hashcat should not write restore files outside the workspace.

Hashcat should not write cracked output outside the workspace.

## Required Hashcat Options Per Job

The command builder should include these Hashcat options for queued jobs:

```text
--session
--restore-file-path
--potfile-path
--outfile
--status
--status-json
--status-timer
```

Recommended status timer:

```text
30 seconds
```

The app should store these options internally as an argument array.

Example internal structure:

```text
[
  "path/to/hashcat",
  "--session",
  "session_job_00042_run_00003",
  "--restore-file-path",
  "hashcat/restore/session_job_00042_run_00003.restore",
  "--potfile-path",
  "hashcat/potfile/workspace.potfile",
  "--outfile",
  "hashcat/output/job_00042_run_00003_outfile.txt",
  "--status",
  "--status-json",
  "--status-timer",
  "30",
  "... remaining job arguments ..."
]
```

The GUI may show a command preview, but the backend should never rely on unsafe raw shell strings.

Command preview files should remain inside the workspace unless the user explicitly exports them elsewhere.

## Process Output Handling

The app should capture Hashcat output while the job runs.

The app should save:

```text
stdout
stderr
status JSON output
app queue events
error messages
```

Suggested files:

```text
hashcat/logs/job_<job_id>_run_<run_id>.log
hashcat/logs/job_<job_id>_run_<run_id>_status.jsonl
logs/queue/queue.log
logs/errors/job_<job_id>_run_<run_id>_error.log
```

The visible log panel may show recent output, but clearing the visible log should not delete saved log files.

Logs may reveal recovery strategy and should stay inside the workspace.

Logs should avoid printing secrets directly when the app controls the text.

Hashcat output files and potfiles may contain cracked passwords and must be treated as sensitive.

## Progress Tracking

The app should update progress from Hashcat status output when available.

Tracked progress may include:

- status text
- percent complete
- recovered count
- speed
- estimated time
- current attack position
- restore point
- device temperature or utilization if reported
- last status timestamp

The app should save the last known progress in queue state.

If status output is missing or cannot be parsed, the app should still keep the job running and log a warning.

A status parse failure should not automatically stop the job.

## Result Detection

When a Hashcat process exits, the app should classify the job before starting the next one.

The app should check:

- Hashcat exit code
- Hashcat final status text
- status JSON, if available
- output file
- workspace potfile
- error log

### cracked

Mark the job as cracked when Hashcat reports success or the output file contains a recovered result for the job.

When a job cracks a target/header:

- mark that job as cracked
- mark the target/header record as cracked so future jobs for it can be skipped or warned
- save the successful job ID on the target/header record
- save the cracked result file path on the target/header record
- automatically skip remaining pending jobs for that same target/header
- apply the queue behavior after successful crack

The app should save:

- target ID
- target display name
- original target path
- normalized header path
- header type, if known
- Hashcat mode
- password found
- PIM used, if VeraCrypt
- keyfiles used, if any
- password source used
- successful job ID
- run attempt ID
- session name
- started timestamp
- cracked timestamp
- output file path
- potfile path
- command argument array path

Cracked result files are sensitive and must stay inside the workspace.

### exhausted

Mark the job as exhausted when Hashcat completes normally and no password was found.

### failed

Mark the job as failed when Hashcat exits with an error or the app cannot determine a safe result.

The app should save the error details and keep the job available for restart.

### skipped

Mark the job as skipped when:

- the user chooses to skip it
- its target/header has already been cracked by another job
- the selected queue behavior stops the queue and later jobs are manually skipped

## Cracked-Target Behavior

The app should not continue running more jobs against the same target/header after that target/header is cracked.

Once a target/header is cracked, the app should:

- mark the successful job as cracked
- mark the target/header as cracked
- record which job cracked it
- record where the cracked result was saved
- skip remaining pending jobs for that same target/header
- continue or stop the queue based on the queue-level setting

This is both a usability rule and a backend tracking rule.

The job record answers:

```text
Which specific attack attempt succeeded?
```

The target/header record answers:

```text
Is this volume already recovered?
Which job recovered it?
Should future jobs for it be skipped or warned?
```

## Queue Behavior After Successful Crack

The app should support only two queue-level choices after a target/header is cracked.

### Continue with other uncracked targets

When a job cracks a target/header:

- mark that job as cracked
- mark the target/header as cracked
- skip remaining pending jobs for that same target/header
- continue with pending jobs for other uncracked targets

This should be the recommended default.

### Stop entire queue

When a job cracks a target/header:

- mark that job as cracked
- mark the target/header as cracked
- skip remaining pending jobs for that same target/header
- save queue state
- stop the queue
- leave other uncracked targets pending

The user may resume the queue later.

## Autosave

The app should auto-save every 60 seconds while a workspace is open.

Autosave files should be stored inside:

```text
queue/autosaves/
```

The current queue state should be stored in:

```text
queue/queue-state.json
```

Suggested autosave file pattern:

```text
queue/autosaves/queue-state_YYYYMMDD_HHMMSS.json
```

The app should use atomic save behavior:

1. Write the new state to a temporary file inside the workspace.
2. Flush and close the file.
3. Rename it over the previous queue state file.
4. Keep the previous valid autosave as fallback.

The app must not use the system temp folder for autosave files.

## Immediate Save Events

The app should save immediately after major changes.

Immediate save events include:

- queue created
- job added to queue
- job removed from queue
- job reordered
- queue started
- job started
- job paused
- job resumed
- pause-after-current enabled
- stop requested
- job stopped and saved
- job stopped and discarded
- job skipped
- job restarted
- job cracked
- target/header marked cracked
- remaining jobs for cracked target/header skipped
- job exhausted
- job failed
- queue completed
- queue behavior after successful crack changed
- Hashcat session created
- restore file created or changed
- output file created or changed
- external path repaired
- app shutdown while queue state exists

## Crash Recovery

On startup, the app should inspect the workspace for interrupted queue activity.

The app should check:

- `queue/queue-state.json`
- latest file in `queue/autosaves/`
- `queue/runner-lock.json`
- active job status
- Hashcat session metadata
- restore file existence
- output file existence
- last known process ID
- last queue log entries

If a job was marked running but no controlled Hashcat process exists, the app should change it to one of these states:

```text
stopped_saved
failed
needs_review
```

Use `stopped_saved` only if a valid restore file appears to exist.

Use `failed` if no restore data exists and the run cannot be resumed.

Use `needs_review` if the app cannot safely decide.

The app should not automatically start Hashcat after crash recovery.

The user should choose Resume, Restart, Skip, or Leave Queue Stopped.

## App Exit While Running

If the user tries to close the app while a job is running, the app should show a clear prompt.

Suggested prompt:

```text
A Hashcat job is currently running.

Choose:
- Pause Now
- Stop and Save
- Stop and Discard
- Cancel Exit
```

The app should not silently leave Hashcat running.

For version 1, the simplest behavior is to require the user to stop or pause the job before the app exits.

If the operating system shuts down unexpectedly, the app should rely on saved queue state and Hashcat restore data during the next startup.

## Workspace State Schema

The exact JSON schema can be finalized during implementation, but the queue state should include:

```text
schema_version
workspace_id
queue_id
queue_status
queue_order
active_job_id
active_run_id
pause_after_current
queue_behavior_after_successful_crack
last_saved_timestamp
last_autosave_timestamp
runner_lock_path
jobs
```

Each job entry should include:

```text
job_id
run_id
target_id
header_id
job_name
status
result
hashcat_session_name
command_array_path
command_preview_path
normalized_header_path
restore_file_path
potfile_path
hashcat_log_path
status_log_path
outfile_path
started_timestamp
ended_timestamp
last_status_timestamp
last_known_progress
resume_available
error_summary
```

The target/header record should include cracked tracking fields:

```text
target_id
header_id
cracked_status
successful_job_id
successful_run_id
cracked_result_path
cracked_timestamp
remaining_jobs_skipped
```

The queue state should not store cracked passwords directly if a separate cracked result file is used.

If the queue state references cracked result files, those files must stay inside the workspace.

## Files Created or Modified

This step may create or modify:

```text
queue/queue-state.json
queue/runner-lock.json
queue/autosaves/*
queue/history/*

jobs/queued/*
jobs/completed/*
jobs/failed/*
jobs/skipped/*
jobs/command-arrays/*
jobs/command-previews/*

targets/targets.json
headers/metadata/*

hashcat/sessions/*
hashcat/restore/*
hashcat/potfile/*
hashcat/logs/*
hashcat/output/*

logs/queue/*
logs/errors/*
logs/app/*

reports/json/*
cleanup/cleanup-manifest.json
temp/active-job/*
```

The app should not create queue runner files outside the workspace.

## Workspace Folders Used

This step uses these workspace folders:

```text
queue/
queue/autosaves/
queue/history/
jobs/queued/
jobs/completed/
jobs/failed/
jobs/skipped/
jobs/command-arrays/
jobs/command-previews/
targets/
headers/metadata/
hashcat/sessions/
hashcat/restore/
hashcat/potfile/
hashcat/logs/
hashcat/output/
logs/queue/
logs/errors/
logs/app/
reports/json/
cleanup/
temp/active-job/
```

Temporary runner files should stay inside:

```text
temp/active-job/
```

The app must not use the operating system temp folder for queue runner state, Hashcat job files, restore files, potfiles, logs, output, or cracked results.

## Safety Rules

The queue runner must follow these rules:

- only support legitimate recovery of user-owned volumes
- never modify original VeraCrypt or TrueCrypt volumes
- never run Hashcat against original full volumes
- only run Hashcat against normalized workspace job headers
- reject jobs whose input header is missing or oversized
- keep restore files inside the workspace
- keep the Hashcat potfile inside the workspace
- keep Hashcat logs inside the workspace
- keep Hashcat output files inside the workspace
- keep cracked results inside the workspace
- keep command arrays inside the workspace
- keep command previews inside the workspace unless explicitly exported
- do not use system temp folders for queue or job data
- do not silently upload, transmit, or exfiltrate anything
- do not claim secure deletion is guaranteed
- describe cleanup as trace centralization and minimization
- use Hashcat as a local backend only
- build commands as argument arrays internally
- never rely on unsafe raw shell strings
- do not hide Hashcat errors from the user
- do not continue to the next job until the current job is safely classified and saved
- do not automatically resume cracking after a crash without user action
- do not continue running jobs for a target/header after that target/header has been cracked

## Open Questions

Open questions for later steps:

- exact final JSON schema for queue state
- exact final JSON schema for job records
- exact final cracked-result file format
- exact UI layout for crash recovery prompts
- exact Hashcat exit-code mapping
- exact status JSON parsing rules
- exact report format for completed queue runs
- exact behavior when the app detects a still-running Hashcat process after app restart
- exact retention limit for autosave history
- exact cleanup screen behavior for obsolete restore and output files
- exact handling if multiple headers later point to the same original target

## Final Decisions

- The app runs one Hashcat job at a time.
- The next job starts only after the current job exits, is classified, and state is saved.
- Queue runner statuses should include pending, running, paused, stopped_saved, cracked, exhausted, failed, and skipped.
- Draft jobs belong to the job builder, not the active queue runner.
- Completed may be a UI grouping, but final job results should be cracked, exhausted, failed, or skipped.
- The queue supports Start Queue.
- The queue supports Pause Now.
- Pause Now pauses the active Hashcat process while keeping it alive.
- The queue supports Pause After Current Job.
- Pause After Current Job lets the active job finish and then stops the queue before starting another job.
- The queue supports Stop and Save.
- Stop and Save preserves restore data when possible.
- The queue supports Stop and Discard.
- Stop and Discard discards resume progress for the current run but does not delete the job definition.
- The queue supports Resume.
- Resume can continue a paused active process or resume from a restore file after restart.
- The queue supports Skip Selected Job.
- The queue supports Restart Selected Job.
- Restart Selected Job should create a new run attempt and a new unique Hashcat session name.
- Each job run must use a unique Hashcat session name.
- Each job run must use a workspace-local restore file.
- The workspace must use its own Hashcat potfile.
- Hashcat logs must stay inside the workspace.
- Hashcat output files must stay inside the workspace.
- Cracked results must stay inside the workspace.
- Queue state must be saved in `queue/queue-state.json`.
- Autosaves must be stored in `queue/autosaves/`.
- The app should auto-save every 60 seconds.
- The app should save immediately after major queue changes.
- Queue saves should use atomic writes inside the workspace.
- The app should use a workspace-local runner lock file to prevent two queue runners from using the same workspace.
- The app should not automatically resume cracking after a crash.
- On startup after interruption, the app should show recovery choices.
- When a job cracks a target/header, the app should mark the job as cracked.
- When a job cracks a target/header, the app should also mark the target/header record as cracked so future jobs for it can be skipped or warned.
- When a target/header is cracked, the app should automatically skip remaining pending jobs for that same target/header.
- The app should not offer an option to keep working the same target/header after it is cracked.
- The queue should have one setting named `Queue behavior after successful crack`.
- The queue behavior after successful crack should have two choices: Continue with other uncracked targets, or Stop entire queue.
- The default queue behavior after successful crack should be Continue with other uncracked targets.
- The app should not start the next job until the current result is saved.
- The app should not silently leave Hashcat running when the user exits.
- Hashcat commands must be stored and run as argument arrays.
- Command strings are only for preview or export.
- The queue runner must not use system temp folders.
- The queue runner must not write sensitive or forensic-trail files outside the workspace by default.
