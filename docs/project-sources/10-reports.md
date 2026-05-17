# 10-reports.md

## Purpose

This step defines reporting for the Portable Hashcat GUI project.

Reports should give the user clear, usable records of cracked results and the exact job details that produced them.

The Reports step must focus only on reporting, cracked-result viewing, report files, and recovery-result packaging.

The Reports step does not redesign:

```text
workspace and portability
Hashcat setup
queue running and resume
header extraction
hash mode building
PIM handling
keyfile handling
password building
final GitHub/Codex build planning
```

Reports may contain recovered passwords, PIM values, keyfile names, header copies, original target paths, command details, and recovery strategy information.

Reports are sensitive project data.

Reports must stay inside the workspace by default.

The app must not claim that deleting reports or the workspace guarantees secure deletion. The app should describe cleanup as trace centralization and minimization.

## Core Reporting Goals

The app should support:

```text
cracked result reports
live cracked-result reporting while the queue is still running
per-target report viewing from the queue
per-cracked-job recovery folders
CSV cracked-results index
JSON structured reports
human-readable reports
GUI result viewer
redacted report copies
report export with warnings
cleanup manifest tracking
```

The app should not make the user wait until the full queue completes before seeing a successful recovery result.

When a job cracks a target/header, the app should immediately generate the available report files and show the user a clear way to open them.

## User Inputs

The Reports screen should accept:

```text
select cracked result
view report
reveal password
copy password
open recovery folder
open report folder
open Hashcat output
open command preview
create redacted copy
export report outside workspace
filter reports by target
filter reports by job
filter reports by cracked time
search reports
add report notes
```

Queue row actions for cracked jobs should include:

```text
View Target Report
Open Recovery Folder
Reveal Password
Copy Password
Open Report Folder
```

The user should also be able to open reports from:

```text
Reports screen
Queue screen
Target details screen
Job details screen
Dashboard recent activity
```

## Report Types

The app should create these report types:

```text
CSV cracked-results index
JSON per-result report
Markdown human-readable per-result report
Plain text quick-result snippet
Optional redacted JSON report
Optional redacted Markdown report
Report index
Recovery package manifest
Mount/open checklist
Stats file
```

Suggested folders:

```text
reports/csv/
reports/json/
reports/markdown/
reports/text/
reports/cracked/
```

Recommended human-readable format:

```text
Markdown
```

Plain text is useful for quick access and recovery-package snippets.

## Live Cracked-Result Reporting

The app should not wait until the entire queue finishes before creating reports.

When a job is classified as cracked, the app should immediately create or update cracked-result reports for that target/header using all information available at that time.

This should happen before the queue starts the next job.

When a job cracks a target/header, the app should:

```text
save the raw cracked result first
mark the job as cracked
mark the target/header as cracked
save the successful job ID on the target/header record
save the cracked result file path on the target/header record
skip remaining pending jobs for that same target/header
create the per-cracked-job recovery folder
copy the successful normalized header into that folder
copy the successful normalized keyfiles into that folder, if keyfiles were used
create the quick result snippet
create the full JSON report
create the human-readable Markdown report
create or update the CSV cracked-results index
create or update the report index
create the stats file
create the recovery package manifest
create the mount/open checklist
update the cleanup manifest
update the queue row with View Report and Open Recovery Folder actions
show a non-blocking popup or notification if the app is open
save workspace state
then continue or stop the queue based on queue behavior
```

Suggested non-blocking popup:

```text
Target cracked: <target name>

Buttons:
- View Report
- Open Recovery Folder
- Dismiss
```

The popup should not block the queue from continuing.

If the user dismisses or misses the popup, the cracked job should still show persistent actions in the queue row and Reports screen.

## Queue Integration

The Queue screen should show report access as soon as a job is cracked.

Suggested queue row display:

```text
Status: Cracked
Result: Available
Buttons:
- View Target Report
- Open Recovery Folder
- Reveal Password
- Copy Password
```

The queue row should keep showing these actions after the queue continues, stops, or completes.

The queue should not start the next job until the cracked result is saved and the minimum report package is created.

Minimum report package before moving on:

```text
raw cracked result saved
job marked cracked
target/header marked cracked
recovered-result.txt created
recovered-result.json created
recovery folder created
cleanup manifest updated
workspace state saved
```

If optional report files fail, the app should preserve the cracked result and continue with a warning.

## Report Failure Handling

The app must never lose a cracked result because report generation failed.

Required rule:

```text
Never lose a cracked result because report generation failed.
```

If Hashcat reports a crack or the output file contains a recovered result, the app should save the raw cracked result before generating optional reports.

Failure handling order:

```text
1. Save raw cracked result.
2. Save job cracked status.
3. Save target/header cracked status.
4. Save minimum cracked-result metadata.
5. Try to generate reports.
6. If report generation fails, log the error and warn the user.
7. Keep the cracked result available for retrying report generation.
```

Suggested warning:

```text
The target was cracked, but one or more report files could not be created. The recovered result was saved. Open Reports to retry report generation.
```

The app should provide:

```text
Retry Report Generation
Open Saved Result
Open Error Log
```

## Per-Cracked-Job Recovery Folder

When a job is classified as cracked, the app should immediately create a dedicated recovery folder for that successful job.

Suggested path:

```text
reports/cracked/job_<job_id>_run_<run_id>/
```

Suggested folder layout:

```text
reports/cracked/job_<job_id>_run_<run_id>/
  recovered-result.txt
  recovered-result.json
  recovered-result.md
  recovery-package-manifest.json
  how-to-open-this-volume.txt
  job-header-512.bin
  command-used.txt
  stats.txt
  keyfiles/
    keyfile_<id>_<safe_name>
```

The folder should contain only the files needed for that successful cracked result.

The folder should not include unrelated files, unrelated wordlists, unrelated candidate lists, unrelated keyfile groups, or unrelated headers.

The recovery folder should be treated as highly sensitive because it may contain:

```text
recovered password
PIM value
header copy
keyfile copies
original target path
Hashcat mode
command details
job metadata
recovery strategy details
```

The recovery folder must stay inside the workspace by default.

## Recovery Folder Header Copy

The per-cracked-job recovery folder should include a copy of the normalized 512-byte job header that was used by the successful Hashcat job.

Suggested filename:

```text
job-header-512.bin
```

Rules:

```text
copy the normalized workspace job header used by the successful job
do not read from the original volume again
do not copy unrelated headers
do not copy the full original volume
track the copied header in the cleanup manifest
```

The report should also include the original workspace-relative header path.

## Recovery Folder Keyfile Copies

If keyfiles were used for the successful job, the recovery folder should contain a `keyfiles/` subfolder.

Suggested path:

```text
reports/cracked/job_<job_id>_run_<run_id>/keyfiles/
```

The app should copy only the normalized workspace keyfiles used by the successful job.

Rules:

```text
copy only successful-job keyfiles
copy normalized workspace keyfiles, not original external keyfiles
do not copy unrelated keyfiles
do not copy unrelated keyfile groups
do not include keyfile contents in logs
track copied keyfiles in the cleanup manifest
```

The goal is to let the user quickly access the recovered volume without digging through the full workspace.

If the keyfile was capped to the first 1 MiB during normalization, the report should state that the copied keyfile is the normalized job keyfile.

## Recovered Result Snippet

Each cracked-job recovery folder should contain a short plain text snippet with only the key result details for that job.

Suggested filename:

```text
recovered-result.txt
```

Suggested contents:

```text
Target: <target display name>
Original path: <original target path>

Container family: <VeraCrypt / TrueCrypt / unknown>
Header type: <header type>
Header file: job-header-512.bin

Password: <recovered password>
PIM: <PIM used, if VeraCrypt, or default / not applicable>
Keyfiles: <keyfiles used, if any>
Hashcat mode: <mode number and name>

Job ID: <job_id>
Run ID: <run_id>
Session: <hashcat session name>

Started: <start time>
Cracked: <cracked time>
Elapsed: <elapsed time>

Candidates tested before crack: <count if known>
Candidates remaining / untested: <count if known>
Speed at crack: <speed if known>
Average speed: <average speed if known>
Restore point at crack: <restore point if known>
Device(s) used: <devices if known>

Hashcat outfile: <path>
Potfile: <path>
Full report: recovered-result.md
Structured report: recovered-result.json
```

If a value is unknown, the app should write:

```text
unknown
```

The app should not guess.

## Full Per-Result JSON Report

Each cracked result should create a full JSON report.

Suggested root report path:

```text
reports/json/cracked_result_<job_id>_<run_id>.json
```

Suggested recovery folder copy:

```text
reports/cracked/job_<job_id>_run_<run_id>/recovered-result.json
```

The JSON report should be the complete structured record.

Suggested structure:

```text
schema_version
report_id
report_type
created_timestamp

target
header
job
run
result
hashcat
inputs
stats
paths
warnings
notes
```

Suggested target fields:

```text
target_id
target_display_name
original_path
source_category
container_family
ownership_confirmed
cracked_status
```

Suggested header fields:

```text
header_id
candidate_type
header_type
normalized_header_path
recovery_folder_header_copy
source_offset
normalized_size
sha256_normalized_header
```

Suggested job fields:

```text
job_id
run_id
job_name
status
hashcat_session_name
command_array_path
command_preview_path
started_timestamp
cracked_timestamp
elapsed_time
```

Suggested result fields:

```text
password_found
pim_used
pim_mode
keyfiles_used
password_source_used
wordlist_used
hashcat_mode
hashcat_mode_name
```

Suggested stats fields:

```text
candidates_tested_before_crack
candidates_remaining_or_untested
candidate_count_total_if_known
speed_at_crack
average_speed
restore_point_at_crack
recovered_count
rejected_count
hashcat_status_at_crack
device_names
device_temperatures_if_reported
attack_mode
```

Suggested paths fields:

```text
recovery_folder_path
outfile_path
potfile_path
hashcat_log_path
status_log_path
stats_file_path
manifest_path
how_to_open_file_path
```

## Human-Readable Report

Each cracked result should create a human-readable Markdown report.

Suggested root report path:

```text
reports/markdown/cracked_result_<job_id>_<run_id>.md
```

Suggested recovery folder copy:

```text
reports/cracked/job_<job_id>_run_<run_id>/recovered-result.md
```

Suggested sections:

```text
Cracked Result Summary
Target
Header Used
Successful Job
Recovered Secret
PIM
Keyfiles
Password Source
Hashcat Settings
Timeline
Stats
Command Used
Recovery Folder Contents
Warnings
Notes
```

The recovered password may be included in the file because the purpose of the report is recovery.

The GUI should still hide the password by default until the user chooses to reveal it.

## CSV Cracked-Results Index

The app should maintain a CSV index of cracked results.

Suggested file:

```text
reports/csv/cracked_results.csv
```

Each cracked result should add or update one row.

Suggested columns:

```text
target_id
target_name
original_path
header_id
header_type
normalized_header_path
container_family
hashcat_mode
hashcat_mode_name
password_found
pim_used
keyfiles_used
password_source
wordlist_used
job_id
run_id
session_name
start_time
cracked_time
elapsed_time
candidates_tested_before_crack
candidates_remaining_or_untested
speed_at_crack
average_speed
recovery_folder_path
outfile_path
potfile_path
command_preview_path
```

The CSV file may expose recovered passwords and must be treated as sensitive.

If the user exports the CSV outside the workspace, the app should show an external-location cleanup warning.

## Report Index

The app should maintain a report index.

Suggested file:

```text
reports/json/report_index.json
```

Suggested fields:

```text
schema_version
updated_timestamp
reports
```

Each report entry should include:

```text
report_id
target_id
header_id
job_id
run_id
created_timestamp
report_type
cracked_status
recovery_folder_path
json_report_path
markdown_report_path
text_result_path
redacted_report_paths
```

The report index helps the Reports screen load quickly without scanning every report file.

## Recovery Package Manifest

Each per-cracked-job recovery folder should include a manifest.

Suggested filename:

```text
recovery-package-manifest.json
```

The manifest should list every file copied or created inside the recovery folder.

Suggested fields:

```text
schema_version
package_id
target_id
header_id
job_id
run_id
created_timestamp
recovery_folder_path
files
source_workspace_paths
warnings
notes
```

Each file entry should include:

```text
file_role
filename
package_relative_path
source_workspace_path
created_timestamp
sha256_if_calculated
sensitivity_category
notes
```

Suggested file roles:

```text
result_snippet
json_report
markdown_report
mount_checklist
stats
command_used
header_copy
keyfile_copy
manifest
```

The manifest should help the user understand what is in the recovery package and what came from where.

The manifest should not replace the cleanup manifest. It is specific to the per-cracked-job recovery folder.

## How-To-Open Checklist

Each per-cracked-job recovery folder should include a simple checklist file.

Suggested filename:

```text
how-to-open-this-volume.txt
```

Purpose:

```text
Give the user the recovered information in one place so they can open their volume without digging through workspace folders.
```

Suggested contents:

```text
Use this recovered information:

Target:
<target display name>

Original volume path:
<original path>

Likely container family:
<VeraCrypt / TrueCrypt / unknown>

Header type:
<normal / hidden / system / hidden system candidate>

Password:
<recovered password>

PIM:
<PIM value, default, or not applicable>

Keyfiles:
<none or keyfiles/ folder>

If keyfiles were used, use the files in:
keyfiles/

Notes:
- Use the original volume, not the copied header, when opening the volume in VeraCrypt or TrueCrypt.
- The copied header is included for reference and recovery recordkeeping.
- If the original path has changed, browse to the original volume or restored volume location.
```

The app should not automatically mount the volume.

The checklist should not claim the volume is guaranteed to open, because the user may still choose the wrong original target, wrong hidden/normal option, wrong mount tool version, or wrong keyfile handling.

## Stats File

Each per-cracked-job recovery folder should include a stats file.

Suggested filename:

```text
stats.txt
```

Stats should be best-effort.

The app should include values from Hashcat status output when available.

If a value cannot be confirmed, write:

```text
unknown
```

Do not guess or invent stats.

Suggested stats:

```text
elapsed time
average speed
speed at crack
candidates tested before crack
estimated candidates remaining / untested
candidate count total, if known
restore point at crack
recovered count
rejected count
Hashcat status at crack
device names
device temperatures, if reported
attack mode
wordlist or generated password source
candidate count for password source
keyfile set ID
PIM value
Hashcat session name
Hashcat mode
```

Suggested wording:

```text
Stats are based on Hashcat output and app metadata. Some values may be unknown if Hashcat did not report them or if the app could not parse them reliably.
```

## Candidate and Untested Counts

Reports should include candidate attempt information when available.

Suggested fields:

```text
candidates_tested_before_crack
candidate_count_total_if_known
candidates_remaining_or_untested
```

Rules:

```text
Use Hashcat status output when available.
Use app-generated candidate counts when reliable.
Do not guess.
If total candidate count is unknown, mark remaining / untested as unknown.
If the crack occurred before exhausting the source, estimate untested only when both tested and total counts are reliable.
```

Suggested report wording:

```text
Candidates tested before crack: <count or unknown>
Candidates remaining / untested: <count or unknown>
```

This is useful because the successful job may end before testing all candidates.

## Command Used

The report should include the command used in two forms:

```text
saved internal argument array path
human-readable command preview path
```

The recovery folder should include:

```text
command-used.txt
```

The app should not rebuild the successful command from memory if the saved command record exists.

It should reference and copy the command preview that was actually used by the successful run.

The command string is only for viewing/export.

The backend should continue using argument arrays internally.

## Keyfiles Used In Reports

Reports should show keyfiles by saved workspace metadata.

For each keyfile used in the successful job, include:

```text
keyfile_id
safe_display_name
normalized_workspace_path
recovery_folder_copy_path
was_capped_to_first_1048576_bytes
keyfile_set_id
keyfile_group_id
```

Do not include keyfile contents in reports, logs, previews, or errors.

The copied keyfiles in the recovery folder are the actual normalized job keyfiles needed for that successful job.

## Password Source Used In Reports

Reports should show the password source used by the successful job.

For generated wordlists, include:

```text
password_set_id
password_source_name
wordlist_path
candidate_count
recipe_path
```

For typed or pasted manual lists, include:

```text
password_set_id
password_source_name
candidate_count
wordlist_path if saved
recipe path
```

For imported wordlists, include:

```text
wordlist_id
workspace_copy_path
line_count if known
```

For external wordlists, include:

```text
external_path
external warning
```

The report should not copy full wordlists into the recovery folder by default.

The recovery folder should contain the result and needed unlock materials, not the entire attack material.

## Result Viewer Inside GUI

The Reports screen should include an internal result viewer.

Suggested layout:

```text
Reports

Cracked Results List:
- target name
- cracked status
- cracked time
- job ID
- run ID
- header type
- mode
- password hidden by default

Selected Result Details:
- target details
- header details
- recovered password, hidden by default
- PIM used
- keyfiles used
- password source used
- command used
- stats
- recovery folder path
- report file paths
```

Suggested buttons:

```text
Reveal Password
Hide Password
Copy Password
Copy PIM
Open Recovery Folder
Open Report Folder
Open Hashcat Output
Open Command Preview
Create Redacted Copy
Export Report
Retry Report Generation
```

The GUI should hide recovered passwords by default.

The GUI may show a warning before reveal:

```text
Revealing the password may expose it on screen.
```

## Redacted Reports

The app should support optional redacted reports for sharing or troubleshooting.

Suggested files:

```text
reports/markdown/cracked_result_<job_id>_<run_id>_redacted.md
reports/json/cracked_result_<job_id>_<run_id>_redacted.json
```

Redacted reports should remove or replace:

```text
password found
PIM, optional
full original path, optional
keyfile names, optional
wordlist names, optional
command paths, optional
personal notes, optional
```

Suggested redaction value:

```text
[redacted]
```

The user should choose what to redact.

Redacted reports should still be treated as potentially sensitive because they may reveal recovery strategy.

## External Export

Reports should stay inside the workspace by default.

If the user deliberately exports a report outside the workspace, the app should show a warning.

Suggested warning:

```text
This report will be saved outside the workspace. At cleanup time, you must remember to delete or securely erase this external location separately. The workspace cleanup process cannot remove files saved elsewhere.
```

External report exports should be recorded in:

```text
cleanup/cleanup-manifest.json
```

The app should mark external reports as:

```text
external
non-portable
user-selected export
```

## Report Notes

The user may add notes to a report.

Notes should be stored inside the report metadata and report file.

Notes may contain sensitive information, so they should stay inside the workspace.

The app should not include notes in redacted reports unless the user chooses to include them.

## Report Regeneration

The app should allow report regeneration from saved cracked-result metadata.

Suggested actions:

```text
Regenerate Missing Reports
Regenerate This Report
Regenerate Recovery Folder
Rebuild CSV Index
Rebuild Report Index
```

Rules:

```text
do not rerun Hashcat
do not read the original volume again
use saved workspace metadata and saved cracked result
do not overwrite user notes unless confirmed
preserve old report copies or write a new generated timestamp if needed
```

## Files Created or Modified

This step may create or modify:

```text
reports/csv/cracked_results.csv

reports/json/report_index.json
reports/json/cracked_result_<job_id>_<run_id>.json
reports/json/cracked_result_<job_id>_<run_id>_redacted.json

reports/markdown/cracked_result_<job_id>_<run_id>.md
reports/markdown/cracked_result_<job_id>_<run_id>_redacted.md

reports/text/cracked_result_<job_id>_<run_id>.txt

reports/cracked/job_<job_id>_run_<run_id>/recovered-result.txt
reports/cracked/job_<job_id>_run_<run_id>/recovered-result.json
reports/cracked/job_<job_id>_run_<run_id>/recovered-result.md
reports/cracked/job_<job_id>_run_<run_id>/recovery-package-manifest.json
reports/cracked/job_<job_id>_run_<run_id>/how-to-open-this-volume.txt
reports/cracked/job_<job_id>_run_<run_id>/job-header-512.bin
reports/cracked/job_<job_id>_run_<run_id>/command-used.txt
reports/cracked/job_<job_id>_run_<run_id>/stats.txt
reports/cracked/job_<job_id>_run_<run_id>/keyfiles/*

targets/targets.json
headers/metadata/header_<header_id>.json
jobs/completed/job_<job_id>.json
queue/queue-state.json

logs/app/*
logs/errors/*
cleanup/cleanup-manifest.json
workspace.json
settings.json
```

Reports should not be created outside the workspace unless the user explicitly exports them.

## Workspace Folders Used

This step uses:

```text
reports/
reports/csv/
reports/json/
reports/markdown/
reports/text/
reports/cracked/

targets/
headers/metadata/
jobs/completed/
jobs/command-arrays/
jobs/command-previews/
queue/

hashcat/output/
hashcat/potfile/
hashcat/logs/

inputs/keyfiles/normalized/
generated/recipes/
generated/wordlists/
inputs/wordlists/imported/
inputs/wordlists/manifests/

logs/app/
logs/errors/
cleanup/
```

This step must not use:

```text
system temp folders
external folders by default
original volume files as report inputs
original keyfile paths as recovery package inputs
```

## App Behavior

The app should:

```text
create reports when a job is cracked
create reports before starting the next queue job
create a per-cracked-job recovery folder
copy the successful normalized 512-byte job header into the recovery folder
copy only the successful normalized keyfiles into the recovery folder, if keyfiles were used
create a short recovered-result.txt snippet
create a full JSON report
create a human-readable Markdown report
create a stats.txt file
create a command-used.txt file
create a recovery-package-manifest.json file
create a how-to-open-this-volume.txt file
update the CSV cracked-results index
update the report index
show a non-blocking popup when a target is cracked
add persistent View Report and Open Recovery Folder actions to the queue row
hide recovered passwords by default in the GUI
allow user-controlled reveal and copy
support redacted report copies
support report export with external-location warning
support report regeneration from saved cracked-result metadata
save report files inside the workspace by default
save immediately after cracked result detection and report creation
update the cleanup manifest
```

## Safety Rules

The Reports step must follow these rules:

```text
only support legitimate recovery of user-owned or authorized volumes
do not crack passwords itself
do not run Hashcat
do not modify original VeraCrypt or TrueCrypt volumes
do not read original volumes again for report generation
do not modify original keyfiles
store reports inside the workspace by default
treat reports as sensitive recovery data
treat recovery folders as highly sensitive
hide recovered passwords by default in the GUI
allow user-controlled password reveal and copy
do not print recovered passwords in normal logs
do not include keyfile contents in logs or report previews
do not copy unrelated keyfiles into recovery folders
do not copy unrelated wordlists or candidate lists into recovery folders
do not save reports outside the workspace unless the user explicitly exports them
warn before external export
record external report exports in the cleanup manifest
do not upload, transmit, or exfiltrate reports, passwords, headers, keyfiles, logs, or results
do not use system temp folders for report generation
do not claim secure deletion is guaranteed
describe cleanup as trace centralization and minimization
never lose a cracked result because report generation failed
```

## Open Questions

Open questions for implementation:

```text
exact final JSON schema for cracked-result reports
exact final CSV column order
exact UI layout for the Reports screen
exact UI layout for queue row report buttons
exact notification style for cracked-result popup
whether password reveal should require a second confirmation
whether copy-to-clipboard should auto-clear after a timeout
whether redacted reports should be generated by default or only on demand
whether recovery folders should include checksums for copied keyfiles and headers
whether stats should include device temperatures by default or only when available
whether report regeneration should overwrite existing reports or create versioned copies
```

## Final Decisions

```text
The Reports step is Step 10.
Reports focus on cracked results and the details needed to understand what succeeded.
Reports must stay inside the workspace by default.
Reports are sensitive because they may contain recovered passwords and recovery strategy details.
Reports should be generated as soon as a job is classified as cracked.
The app should not wait until the entire queue completes before making cracked-result reports available.
When a target/header is cracked, the app should immediately create or update the available report files.
The queue row should show persistent View Report and Open Recovery Folder actions for cracked jobs.
The app may show a non-blocking popup when a job cracks a target/header.
The cracked-result popup should not block the queue from continuing.
The app should create a per-cracked-job recovery folder.
The recovery folder should be created before the queue starts the next job.
The recovery folder should include a copy of the normalized 512-byte job header used by the successful job.
The recovery folder should include a short recovered-result.txt snippet.
The recovery folder should include the full JSON report.
The recovery folder should include the human-readable Markdown report.
The recovery folder should include command-used.txt.
The recovery folder should include stats.txt.
The recovery folder should include recovery-package-manifest.json.
The recovery folder should include how-to-open-this-volume.txt.
If keyfiles were used, the recovery folder should include a keyfiles/ subfolder.
The keyfiles/ subfolder should contain only the normalized workspace keyfiles needed for the successful job.
The app should copy normalized workspace keyfiles, not original external keyfiles.
The app should not copy unrelated keyfiles, unrelated headers, unrelated wordlists, or unrelated candidate lists into the recovery folder.
The report should include container name and original path.
The report should include extracted and normalized header paths.
The report should include header type.
The report should include Hashcat mode number and name.
The report should include the password found.
The report should include PIM used for VeraCrypt jobs.
The report should include keyfiles used, if any.
The report should include wordlist or password source used.
The report should include job ID and run attempt ID.
The report should include start time, cracked time, and elapsed time.
The report should include useful stats when available.
Stats should be best-effort and should say unknown when the value cannot be confirmed.
The report should include candidates tested before cracking when known.
The report should include candidates remaining or untested when known.
The report should not guess candidate counts or speed values.
The command used should reference the saved argument array and command preview from the successful job.
The app should not rebuild the successful command from memory if the saved command record exists.
The app should create CSV, JSON, and human-readable reports.
Markdown is the preferred human-readable format.
The CSV report should act as a cracked-results index.
The JSON report should be the full structured record.
Each cracked result should have its own report files.
The Reports screen should include an internal GUI result viewer.
The result viewer should hide recovered passwords by default.
The user should be able to reveal or copy the password.
The app should support optional redacted reports.
Redacted reports should remove or hide recovered passwords and other selected sensitive fields.
External report export should be allowed only by deliberate user action.
External exports should show a cleanup warning.
External report paths should be recorded in the cleanup manifest.
Reports should never include keyfile contents.
Reports should not print recovered passwords in normal logs.
The cleanup manifest should track report files and recovery folder files.
The app must never lose a cracked result because report generation failed.
If report generation fails, the app should preserve the cracked result first, log the report error, warn the user, and allow report regeneration.
```
