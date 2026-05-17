# 07-pim-builder.md

## Purpose

This step defines how the app handles VeraCrypt PIM values.

The PIM builder does not crack passwords, extract headers, choose Hashcat modes, handle keyfiles, build password lists, run Hashcat, or manage the queue.

Its job is to let the user enter known or possible VeraCrypt PIM values, expand them into clean integer lists, save those lists inside the workspace, and connect each PIM value to later job generation.

Hashcat supports VeraCrypt PIM start and stop options using:

```text
--veracrypt-pim-start
--veracrypt-pim-stop
```

For a single exact PIM, the app should set both options to the same value.

## Core Rule

PIM applies to VeraCrypt only.

TrueCrypt jobs should not use PIM options.

If the selected hash mode set is TrueCrypt-only, the PIM builder should be disabled or marked as not applicable.

If the selected mode set includes both VeraCrypt and TrueCrypt possibilities, PIM values should only be applied to the VeraCrypt job variants.

## User Inputs

The PIM builder should accept:

```text
No custom PIM / use default behavior
One exact PIM value
Multiple exact PIM values
Simple ranges
Comma-separated input
Newline-separated input
Mixed comma and newline input
```

Examples:

```text
485
789-805
485, 486, 487
485
486
487
485, 789-805, 900
```

The user should not need to create a separate file manually.

## Default PIM Option

The app should include a clear option:

```text
No custom PIM / use VeraCrypt default
```

This is needed because VeraCrypt does not require the user to specify a PIM. If no PIM is specified, VeraCrypt uses default KDF parameters. VeraCrypt also treats an empty PIM or PIM value 0 as default behavior.

The app should store this internally as:

```text
pim_mode: default
```

It should not store it as:

```text
pim_value: 0
```

Reason:

```text
0 is a VeraCrypt default-behavior signal, but the app should avoid mixing “default PIM behavior” with real positive PIM guesses.
```

## Exact PIM Values

The user may enter one or more exact PIM values.

Examples:

```text
12
98
485
231
```

Exact values should be validated as positive integers.

Accepted:

```text
1
12
98
485
1000
```

Rejected:

```text
0
-1
1.5
abc
12a
```

If the user wants default behavior, they should use the explicit default option instead of entering `0`.

## Range Input

The app should support simple inclusive ranges.

Example:

```text
789-805
```

This expands to:

```text
789
790
791
792
793
794
795
796
797
798
799
800
801
802
803
804
805
```

Rules:

```text
Ranges are inclusive.
Start and stop must both be positive integers.
Start must be less than or equal to stop.
Whitespace around the dash is allowed.
```

Accepted:

```text
789-805
789 - 805
1-5
```

Rejected:

```text
805-789
0-10
-5-10
abc-900
789-
```

## Mixed Input

The app should allow mixed exact values and ranges.

Example:

```text
485, 789-805, 900
```

The app should parse this as:

```text
485
789
790
791
792
793
794
795
796
797
798
799
800
801
802
803
804
805
900
```

Input may be separated by:

```text
commas
newlines
commas and newlines together
extra spaces
```

## Expansion Behavior

When the user enters PIM text, the app should:

```text
split by comma and newline
trim whitespace
detect exact values
detect simple ranges
validate all values
expand ranges
deduplicate values
sort values ascending
show preview
save only after user confirms
```

Example input:

```text
805, 789-792, 790, 485
```

Expanded result:

```text
485
789
790
791
792
805
```

## Deduplication and Sorting

The expanded PIM list should always be deduplicated and sorted.

This prevents duplicate jobs.

Example:

```text
Input:
485, 485, 486, 480-486

Expanded:
480
481
482
483
484
485
486
```

The preview should show:

```text
Original entries
Expanded count before deduplication
Duplicates removed
Final PIM count
Final sorted PIM list
```

## Validation Rules

The PIM builder should validate before saving.

Required validation:

```text
value must be an integer
value must be positive
range start must be positive
range stop must be positive
range start must be less than or equal to range stop
expanded list must not be empty unless default mode is selected
```

The app should show clear errors.

Examples:

```text
Invalid PIM value: abc
PIM values must be positive integers.
Invalid range: 805-789. Range start must be less than or equal to range stop.
Use “No custom PIM / use VeraCrypt default” instead of entering 0.
```

## Large Range Warning

Large PIM lists can multiply job count.

The app should warn when a PIM expansion creates many values.

Suggested warning threshold:

```text
More than 100 PIM values
```

Suggested warning:

```text
This PIM list contains 250 values. Each PIM may create separate Hashcat job variants. This can greatly increase queue size and runtime.
```

The app should allow the user to continue after confirmation.

## VeraCrypt PIM Notes

The UI should explain PIM simply:

```text
PIM is a VeraCrypt setting that changes the key derivation work factor. If the wrong PIM is used, the correct password will not open the volume.
```

VeraCrypt describes PIM as the Personal Iterations Multiplier. It controls computational parameters used by the header key derivation function.

The app should not ask the user to understand the math.

The app should not calculate security strength.

The app should not recommend attack ranges as if they are guaranteed.

## Hashcat Job Option Behavior

Each final PIM value should become its own job option variant.

For exact PIM value `485`, the later command builder should add:

```text
--veracrypt-pim-start
485
--veracrypt-pim-stop
485
```

Internal argument-array example:

```text
[
  "--veracrypt-pim-start",
  "485",
  "--veracrypt-pim-stop",
  "485"
]
```

The app should not build unsafe raw shell strings.

Command preview strings may be shown later, but the stored internal form should remain an argument array.

## Default PIM Job Behavior

If the user selects:

```text
No custom PIM / use VeraCrypt default
```

The later command builder should omit custom PIM arguments unless Hashcat requires explicit default values for the selected mode.

If implementation testing shows that Hashcat needs explicit defaults for a certain VeraCrypt mode, that behavior should be handled in the command builder, not by storing fake PIM values in the PIM list.

## PIM and TrueCrypt

TrueCrypt does not use VeraCrypt PIM.

Behavior:

```text
TrueCrypt-only mode set:
  PIM builder disabled or not applicable

VeraCrypt-only mode set:
  PIM builder enabled

Both / Unknown mode set:
  PIM values apply only to VeraCrypt-expanded modes
  TrueCrypt-expanded modes omit PIM options
```

The preview should make this clear.

Suggested wording:

```text
PIM values will be applied only to VeraCrypt job variants. TrueCrypt job variants do not use PIM.
```

## PIM and Argon2id

If a VeraCrypt Argon2id mode is selected in Step 6, PIM still matters.

VeraCrypt documents that Argon2id uses PIM to control memory cost and time cost parameters, with default Argon2id behavior equivalent to PIM 12.

The PIM builder should not need a separate Argon2id UI.

It should only record selected PIM values.

The mode builder and command builder decide which Hashcat modes support Argon2id.

## Preview Before Saving

The PIM builder should show a preview before saving.

Preview should include:

```text
Selected target
Selected header
Selected mode set
PIM mode
Original user input
Expanded PIM values
Duplicate count removed
Final PIM count
Warnings
Output file path
```

Example preview:

```text
PIM mode: custom list
Input: 485, 789-805
Expanded PIM count: 18
Duplicates removed: 0
Saved list: generated/pim-lists/pim_list_<id>.txt
```

## Saved PIM List

Expanded PIM lists should be saved inside the workspace.

Suggested folder:

```text
generated/pim-lists/
```

Suggested filename:

```text
pim_list_<pim_set_id>.txt
```

Suggested content:

```text
485
789
790
791
792
793
794
795
796
797
798
799
800
801
802
803
804
805
```

The file should contain one PIM value per line.

Default PIM mode does not need a list file unless the app wants to save a metadata file saying default mode was selected.

## PIM Metadata

Each PIM set should have metadata stored inside the workspace.

Suggested folder:

```text
generated/recipes/
```

Suggested filename:

```text
pim_set_<pim_set_id>.json
```

Suggested fields:

```text
schema_version
pim_set_id
target_id
header_id
mode_set_id
created_timestamp
updated_timestamp
pim_mode
raw_input
expanded_values
expanded_count
duplicates_removed
sort_order
pim_list_path
warnings
notes
```

Suggested `pim_mode` values:

```text
default
custom_list
not_applicable_truecrypt
```

## Connecting PIM Sets to Job Drafts

The PIM builder should update the job draft metadata.

A job draft should reference:

```text
pim_set_id
pim_mode
pim_list_path
expanded_pim_count
```

The PIM builder should not create final queue jobs by itself.

Final job expansion happens later when hash modes, PIMs, keyfiles, and password sources are combined.

## Job Count Awareness

The PIM builder should show only PIM-related multiplication.

Example:

```text
Runnable VeraCrypt modes: 9
PIM values: 18
PIM-expanded VeraCrypt job variants: 162
```

It should not calculate the full final queue count across passwords and keyfiles.

That belongs to later steps.

## UI Behavior

Suggested PIM Builder screen:

```text
PIM Builder

Target:
  <target name>

Header:
  <header candidate>

Mode set:
  <mode set summary>

PIM options:
  [ ] No custom PIM / use VeraCrypt default
  [ ] Enter exact PIM values or ranges

Input box:
  485, 789-805

Buttons:
  Preview Expanded PIM List
  Save PIM Set
  Clear
  Cancel
```

If the selected mode set is TrueCrypt-only:

```text
PIM Builder

PIM does not apply to TrueCrypt jobs.
No PIM list will be created.
```

## Files Created or Modified

This step may create or modify:

```text
generated/pim-lists/pim_list_<pim_set_id>.txt
generated/recipes/pim_set_<pim_set_id>.json
jobs/drafts/job_<job_id>.json
jobs/command-previews/pim_preview_<job_id>.txt
headers/metadata/header_<header_id>.json
targets/targets.json
logs/app/*
logs/errors/*
cleanup/cleanup-manifest.json
workspace.json
settings.json
```

## Workspace Folders Used

This step uses:

```text
generated/pim-lists/
generated/recipes/
jobs/drafts/
jobs/command-previews/
headers/metadata/
targets/
logs/app/
logs/errors/
cleanup/
```

This step must not use:

```text
system temp folders
external folders by default
original volume files
```

## App Behavior

The app should:

```text
load the selected target, header, and hash mode set
detect whether PIM applies
disable PIM for TrueCrypt-only jobs
allow default VeraCrypt PIM behavior
allow exact positive integer PIM values
allow inclusive ranges
allow comma-separated input
allow newline-separated input
allow mixed input
expand ranges
deduplicate values
sort values ascending
validate positive integers
reject 0 as a custom PIM value
tell the user to use default mode instead of 0
show preview before saving
warn about large expanded PIM lists
save expanded PIM lists inside the workspace
save PIM metadata inside the workspace
update job draft metadata
save immediately after creating or changing a PIM set
update the cleanup manifest
```

## Safety Rules

The PIM builder must follow these rules:

```text
only support legitimate recovery of user-owned or authorized volumes
do not crack passwords itself
do not run Hashcat
do not modify original VeraCrypt or TrueCrypt volumes
do not use original target files
work only from saved workspace target/header/job metadata
store PIM lists inside the workspace
store PIM metadata inside the workspace
treat PIM values as sensitive recovery strategy data
do not use system temp folders
do not save PIM lists outside the workspace unless the user explicitly exports them later
do not upload, transmit, or exfiltrate PIM values, headers, metadata, jobs, logs, or results
do not claim secure deletion is guaranteed
describe cleanup as trace centralization and minimization
```

## Open Questions

Open questions for later steps:

```text
exact final job expansion logic when hash modes, PIMs, keyfiles, and password sources are combined
whether the command builder should ever use Hashcat PIM ranges directly for adjacent PIM values
whether to keep one Hashcat job per PIM always, or allow an advanced range optimization later
exact UI warning threshold for very large PIM lists
exact report formatting for PIM values used in successful jobs
```

## Final Decisions

```text
The PIM builder is Step 7.
The PIM builder handles VeraCrypt PIM values only.
TrueCrypt jobs do not use PIM.
The PIM builder must not redesign hash mode selection, keyfile handling, password building, queue running, or reports.
The app should support “No custom PIM / use VeraCrypt default.”
Default PIM behavior should be stored as pim_mode: default, not as PIM value 0.
The app should reject 0 as a custom PIM guess and tell the user to use default mode instead.
The app should accept exact positive integer PIM values.
The app should accept inclusive ranges such as 789-805.
The app should accept comma-separated input.
The app should accept newline-separated input.
The app should accept mixed comma and newline input.
The app should expand ranges.
The app should deduplicate expanded values.
The app should sort expanded values ascending.
The app should validate that all custom PIM values are positive integers.
The app should show a preview before saving.
The app should warn when a PIM list is large enough to greatly increase job count.
Each exact PIM value should become its own Hashcat job option variant.
For a single exact PIM, the command builder should set --veracrypt-pim-start and --veracrypt-pim-stop to the same value.
The PIM builder should save expanded PIM lists in generated/pim-lists/.
The PIM builder should save PIM metadata in generated/recipes/.
PIM values should be treated as sensitive recovery strategy data.
PIM files should stay inside the workspace by default.
The app must not use system temp folders for PIM data.
The PIM builder should update job draft metadata but should not create final queue jobs by itself.
Final queue expansion happens later after hash modes, PIMs, keyfiles, and password sources are combined.
```

## Reference Notes

```text
Hashcat wiki:
https://hashcat.net/wiki/doku.php?id=hashcat

Hashcat options confirmed:
--veracrypt-pim-start
--veracrypt-pim-stop

VeraCrypt PIM documentation:
https://veracrypt.io/en/Personal%20Iterations%20Multiplier%20%28PIM%29.html

VeraCrypt notes confirmed:
PIM stands for Personal Iterations Multiplier.
PIM controls computational parameters used by the header key derivation function.
PIM is not mandatory.
Leaving PIM empty or setting it to 0 makes VeraCrypt use default KDF parameters.
Argon2id default parameters are equivalent to PIM 12.
```
