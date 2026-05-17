# 08-keyfile-builder.md

## Purpose

This step defines how the app handles VeraCrypt and TrueCrypt keyfiles.

The Keyfile Builder does not crack passwords, extract headers, choose hash modes, handle PIM values, build password lists, run Hashcat, or manage the queue.

Its job is to let the user choose whether keyfiles are needed, import keyfiles into the workspace, normalize them into job-ready workspace-local keyfiles, create keyfile sets, optionally generate keyfile combinations from folders, save keyfile metadata, and connect each keyfile set to later job generation.

The app must never modify original keyfiles.

Hashcat jobs should not use original keyfile paths directly by default.

Hashcat jobs should use normalized workspace keyfile copies.

## Core Rule

Keyfiles are optional.

The app must support:

```text
No keyfiles
Exact selected keyfiles
All files in a folder as one keyfile set
Generated keyfile combinations from a folder
Multiple saved keyfile groups
Priority ordering between keyfile groups
Deduplication of combinations already covered by earlier groups
```

Each final keyfile set becomes its own job option variant.

The Keyfile Builder should update job draft metadata but should not create final queue jobs by itself.

Final queue expansion happens later after hash modes, PIMs, keyfiles, and password sources are combined.

## User Inputs

The Keyfile Builder should accept:

```text
No keyfiles
Select exact keyfile files
Select folder and use all files as one keyfile set
Select folder and generate combinations
Minimum keyfiles per combination
Maximum keyfiles per combination
Optional include no-keyfiles variant
Optional import full copies for browsing and thumbnails
Optional create image thumbnails for photo-type keyfiles
Keyfile group name
Keyfile group priority/order
Deduplicate this group against earlier groups
Preview keyfile sets
Save keyfile set or group
```

Suggested UI choices:

```text
Keyfile options:
  [ ] No keyfiles
  [ ] Use selected keyfiles as one exact set
  [ ] Use all files in a folder as one keyfile set
  [ ] Generate combinations from files in a folder
```

Optional checkboxes:

```text
[ ] Also include a no-keyfiles job variant
[ ] Import full copies for browsing and thumbnails
[ ] Generate workspace-local thumbnails for image keyfiles
[ ] Skip combinations already covered by earlier keyfile groups
```

## No Keyfiles

The app should support a clear no-keyfiles mode.

Internal value:

```text
keyfile_mode: none
```

Expected later command behavior:

```text
No --truecrypt-keyfiles option
No --veracrypt-keyfiles option
```

This should be the simplest path and the default unless the user chooses keyfiles.

## Keyfile Normalization

Keyfiles must be imported as read-only source files and normalized into workspace-local job keyfiles before use.

Original keyfiles are read-only sources.

Hashcat jobs use normalized workspace keyfile copies.

Large keyfiles are reduced to their first 1 MiB.

Small keyfiles are copied exactly as-is.

During import, the app creates a normalized keyfile copy inside the workspace:

```text
If the original keyfile is 1,048,576 bytes or smaller:
  Copy the entire file byte-for-byte.

If the original keyfile is larger than 1,048,576 bytes:
  Copy only the first 1,048,576 bytes byte-for-byte.
```

The app must not:

```text
hash keyfile data as a replacement for the keyfile
compress keyfile data
re-encode keyfile data
pad small files
trim small files
resize image files used as keyfiles
strip metadata from files used as keyfiles
change line endings
normalize text encoding
otherwise transform normalized job keyfile data
```

The normalized keyfile copy must preserve the exact bytes used for VeraCrypt or TrueCrypt keyfile processing.

The app should preserve the selected keyfile set exactly as chosen by the user in the saved group definition.

The app should use normalized workspace keyfile copies in Hashcat jobs.

Suggested normalized keyfile folder:

```text
inputs/keyfiles/normalized/
```

VeraCrypt and TrueCrypt keyfile handling only uses the first 1 MiB of each keyfile. A byte-for-byte copy of that used portion is equivalent for job use while avoiding direct use of the original file.

This keeps job inputs inside the workspace and reduces the chance of damaging, moving, locking, or depending on original keyfiles.

## Workspace Keyfile Folder Layout

Suggested workspace layout:

```text
inputs/keyfiles/
  normalized/
  imported-full/
  thumbnails/
  manifests/
```

### normalized/

Stores job-ready normalized keyfiles.

Hashcat jobs use files from this folder.

### imported-full/

Stores optional full copies of selected keyfiles for user browsing, visual recognition, and thumbnail support.

Full copies are not used directly by Hashcat jobs.

### thumbnails/

Stores optional workspace-local thumbnails generated from image-type full imports.

Thumbnails are not used by Hashcat jobs.

### manifests/

Stores imported keyfile metadata, group metadata, and keyfile set metadata.

## Optional Full-Copy Import for Browsing

The app should include an optional checkbox:

```text
Import full copy for browsing and thumbnails
```

Purpose:

```text
This helps users recognize photo or document keyfiles by thumbnail or preview instead of manually comparing filenames.
```

Rules:

```text
Full copies are optional.
Full copies stay inside the workspace.
Full copies are not used by Hashcat jobs.
Hashcat jobs still use only normalized keyfile copies.
Full-copy imports should be tracked in the cleanup manifest.
```

Suggested full-copy folder:

```text
inputs/keyfiles/imported-full/
```

The app should warn before importing full copies:

```text
Full keyfile copies may reveal private file contents and can increase workspace size. They will be stored inside the workspace for easier cleanup, but secure deletion is not guaranteed.
```

## Optional Thumbnail Support

The app may generate thumbnails for recognizable image keyfiles when the user enables full-copy import.

Suggested checkbox:

```text
Generate workspace-local thumbnails for image keyfiles
```

Rules:

```text
Thumbnails are optional.
Thumbnails are generated only from full workspace-local copies, not from original external files.
Thumbnails stay inside the workspace.
Thumbnails are not used by Hashcat jobs.
Thumbnails are tracked in the cleanup manifest.
Thumbnails should not be written to operating system thumbnail caches.
Thumbnails should not be written to system temp folders.
```

Suggested thumbnail folder:

```text
inputs/keyfiles/thumbnails/
```

Thumbnails are sensitive because they may reveal private image content.

The app should not create thumbnails unless the user enables the option.

## Exact Selected Keyfiles

The user may select one or more exact keyfiles.

The app should:

```text
open each selected keyfile read-only
create a normalized workspace keyfile copy
optionally create a full workspace copy if the user enables full-copy import
optionally create a thumbnail if enabled and supported
never modify the original keyfile
store metadata for each imported keyfile
create one keyfile set containing the selected keyfiles
save the keyfile set metadata
use normalized workspace keyfile copies for jobs
```

For files up to 1,048,576 bytes:

```text
copy the full file byte-for-byte into inputs/keyfiles/normalized/
```

For files larger than 1,048,576 bytes:

```text
copy only the first 1,048,576 bytes byte-for-byte into inputs/keyfiles/normalized/
record that the normalized copy is capped
use the capped workspace copy for Hashcat jobs
```

The app should not use the original keyfile path in generated Hashcat jobs by default.

## Folder as One Keyfile Set

The user may select a folder and use its eligible files as one keyfile set.

The app should not pass the folder path directly to Hashcat.

Instead, it should:

```text
scan the selected folder
show eligible files before import
exclude subfolders by default
create normalized workspace keyfile copies
optionally create full workspace copies if enabled
optionally create thumbnails if enabled and supported
create one keyfile set containing all selected eligible files
save a manifest snapshot of the folder contents
use the normalized workspace keyfile set for jobs
```

Folder import should be treated as a snapshot at import time.

Suggested wording:

```text
The app will import the current files from this folder as a fixed keyfile set. Later changes to the original folder will not change this saved job unless you re-import the folder.
```

This avoids relying on a live folder path whose contents may change later.

## Folder Scan Rules

Default folder scan behavior:

```text
include regular files only
exclude folders
exclude subfolders by default
show hidden/system files as a clear option instead of silently including or excluding them
sort files deterministically
show the final eligible file list before importing
```

Optional advanced settings:

```text
Include files from subfolders
Include hidden/system files
```

If subfolder support is added, the app should still snapshot and normalize files into the workspace before jobs are generated.

The app should not silently use operating system thumbnail caches or external preview caches.

## Generate Keyfile Combinations From Folder

The user may select a folder and generate combinations from its files.

This is for cases where the user knows the keyfile may be one or more files from a folder, but does not know the exact set.

The app should:

```text
scan the selected folder
show the number of eligible files
normalize eligible files into the workspace
optionally import full copies for browsing if enabled
optionally generate thumbnails if enabled
let the user choose minimum keyfiles per combination
let the user choose maximum keyfiles per combination
generate combinations, not permutations
deduplicate identical combinations
sort combinations deterministically
show a preview before saving
save generated keyfile set lists inside the workspace
```

Keyfile order should not matter for this builder.

The app should not create both:

```text
file1,file2
file2,file1
```

Only one combination should be created.

## Min and Max Keyfiles Per Combination

The combination builder should validate:

```text
minimum must be a positive integer
maximum must be a positive integer
minimum must be less than or equal to maximum
maximum must be less than or equal to the number of eligible imported files
minimum should normally be at least 1
```

Example:

```text
Folder has 10 eligible files
min = 1
max = 3

Generated sets:
all 1-file combinations
all 2-file combinations
all 3-file combinations
```

If the user wants to also try no keyfiles, that should be handled by the separate checkbox:

```text
Also include a no-keyfiles job variant
```

Do not treat `min = 0` as normal combination behavior.

## Combination Count Warning

The app should calculate and show the number of generated keyfile sets before saving.

Example:

```text
Folder files: 20
Minimum keyfiles per set: 1
Maximum keyfiles per set: 3

Generated keyfile sets:
C(20,1) + C(20,2) + C(20,3)
20 + 190 + 1140 = 1350 keyfile sets
```

The app should warn when the generated set count is large.

Suggested warning threshold:

```text
More than 100 keyfile sets
```

Suggested warning:

```text
This will create 1,350 keyfile sets. Each set may create separate Hashcat job variants. This can greatly increase queue size and runtime.
```

The user may continue after confirmation.

## Keyfile Groups

The app should support multiple saved keyfile groups.

A keyfile group is a named collection or combination plan for keyfiles.

Examples:

```text
Group 1: small folder, 5 files
Group 2: medium folder, same 5 files plus 6 more
Group 3: large folder, same 11 files plus 8 more
```

This supports cases where the user knows that one folder was more likely used for a specific volume than another folder.

Each group should have:

```text
keyfile_group_id
display_name
source_folder_or_files
priority_order
keyfile_ids
normalized_keyfile_paths
combination_rules
generated_combination_count
dedupe_against_prior_groups
notes
```

The user should be able to order groups from most likely to least likely.

Suggested UI labels:

```text
Try this group before larger groups
Move group up
Move group down
Skip combinations already covered by earlier groups
```

## Deduplication Across Groups

Later groups may skip combinations already generated by earlier groups.

Behavior:

```text
Group 1 generates its combinations.
Group 2 generates combinations but skips exact combinations already covered by Group 1.
Group 3 generates combinations but skips exact combinations already covered by Groups 1 and 2.
```

This prevents wasting time retrying the same keyfile combinations from larger folders.

Deduplication should compare normalized keyfile content identity, not only filenames.

Suggested combination signature:

```text
sorted list of normalized_sha256 values for the keyfiles in the set
```

Reason:

```text
If two files normalize to the same first 1 MiB, they are equivalent for VeraCrypt / TrueCrypt job use.
```

Important rule:

```text
Do not delete or alter the user’s saved groups.
Deduplication only affects generated job variants.
```

The app should show skipped duplicate counts in the preview.

Example:

```text
Group 2 generated combinations before dedupe: 66
Already covered by earlier groups: 15
New combinations to add: 51
```

## Job Count Awareness

The Keyfile Builder should show keyfile-related multiplication.

For VeraCrypt:

```text
Runnable VeraCrypt modes × PIM values × keyfile sets = keyfile-expanded VeraCrypt job variants
```

For TrueCrypt:

```text
Runnable TrueCrypt modes × keyfile sets = keyfile-expanded TrueCrypt job variants
```

If the mode set includes both VeraCrypt and TrueCrypt, the preview should show both separately.

Example:

```text
Runnable VeraCrypt modes: 9
PIM values: 18
Keyfile sets: 4
VeraCrypt keyfile-expanded variants: 648

Runnable TrueCrypt modes: 6
Keyfile sets: 4
TrueCrypt keyfile-expanded variants: 24
```

The Keyfile Builder should not calculate final queue count across password sources.

That belongs to Step 9 and the later final job expansion.

## Hashcat Option Behavior

For VeraCrypt job variants that use keyfiles, the later command builder should add:

```text
--veracrypt-keyfiles
file1,file2
```

Internal argument-array example:

```text
[
  "--veracrypt-keyfiles",
  "inputs/keyfiles/normalized/keyfile_001.bin,inputs/keyfiles/normalized/keyfile_002.bin"
]
```

For TrueCrypt job variants that use keyfiles, the later command builder should add:

```text
--truecrypt-keyfiles
file1,file2
```

Internal argument-array example:

```text
[
  "--truecrypt-keyfiles",
  "inputs/keyfiles/normalized/keyfile_001.bin,inputs/keyfiles/normalized/keyfile_002.bin"
]
```

The app should store command arguments as arrays internally.

Command preview strings may be shown later, but the backend should not rely on unsafe raw shell strings.

## VeraCrypt and TrueCrypt Handling

The Keyfile Builder should work for both VeraCrypt and TrueCrypt.

Behavior:

```text
VeraCrypt-only mode set:
  use --veracrypt-keyfiles for keyfile job variants

TrueCrypt-only mode set:
  use --truecrypt-keyfiles for keyfile job variants

Both / Unknown mode set:
  use --veracrypt-keyfiles for VeraCrypt-expanded job variants
  use --truecrypt-keyfiles for TrueCrypt-expanded job variants
```

The preview should make this clear.

Suggested wording:

```text
Keyfile sets will be applied to both VeraCrypt and TrueCrypt job variants. VeraCrypt jobs will use --veracrypt-keyfiles. TrueCrypt jobs will use --truecrypt-keyfiles.
```

## Keyfile Import Behavior

The app should normalize keyfiles into:

```text
inputs/keyfiles/normalized/
```

Optional full copies should be stored in:

```text
inputs/keyfiles/imported-full/
```

Optional thumbnails should be stored in:

```text
inputs/keyfiles/thumbnails/
```

Suggested normalized filename pattern:

```text
keyfile_<keyfile_id>_<safe_original_name>
```

For normalized large keyfiles:

```text
keyfile_<keyfile_id>_<safe_original_name>_first_1048576.bin
```

The app should avoid unsafe filename characters and should store workspace-internal paths as relative paths.

The original keyfile should never be modified.

The app should not print keyfile contents in logs, previews, reports, or errors.

## Keyfile Metadata

Each imported keyfile should have metadata stored in:

```text
inputs/keyfiles/manifests/
```

Suggested filename:

```text
keyfile_<keyfile_id>.json
```

Suggested fields:

```text
schema_version
keyfile_id
original_path
original_size
normalized_path
normalized_size
normalized_sha256
was_capped_to_first_1048576_bytes
optional_full_import_path
optional_full_import_size
optional_thumbnail_path
safe_display_name
import_timestamp
source_modified_timestamp
source_type
used_in_jobs
notes
```

Suggested `source_type` values:

```text
selected_file
folder_snapshot
folder_combination_source
```

The metadata should not store keyfile contents.

The SHA-256 value is only for workspace integrity checking, duplicate detection, and cleanup tracking.

The app must not use a hash value as a replacement for keyfile bytes.

## Keyfile Set Storage

Each saved keyfile set should have metadata stored in:

```text
generated/recipes/
```

Suggested filename:

```text
keyfile_set_<keyfile_set_id>.json
```

Suggested fields:

```text
schema_version
keyfile_set_id
keyfile_group_id
target_id
header_id
mode_set_id
pim_set_id
created_timestamp
updated_timestamp
keyfile_mode
source_method
keyfile_ids
normalized_keyfile_paths
combination_signature
keyfile_count
hashcat_family_applicability
warnings
notes
```

Suggested `keyfile_mode` values:

```text
none
exact_set
folder_as_single_set
folder_combinations
```

Suggested `source_method` values:

```text
none
selected_files
folder_snapshot
generated_combinations
```

## Keyfile Group Storage

Each saved keyfile group should have metadata stored in:

```text
generated/recipes/
```

Suggested filename:

```text
keyfile_group_<keyfile_group_id>.json
```

Suggested fields:

```text
schema_version
keyfile_group_id
display_name
target_id
header_id
mode_set_id
pim_set_id
created_timestamp
updated_timestamp
priority_order
source_method
source_folder_original_path
source_selected_files
keyfile_ids
normalized_keyfile_paths
combination_mode
min_keyfiles_per_set
max_keyfiles_per_set
generated_count_before_dedupe
duplicates_skipped_against_prior_groups
final_new_keyfile_set_count
dedupe_against_prior_groups
keyfile_set_ids
warnings
notes
```

## Generated Keyfile Lists

For generated combinations, the app should save keyfile set lists inside:

```text
generated/keyfile-lists/
```

Suggested filename:

```text
keyfile_combinations_<keyfile_group_id>.json
```

Suggested fields:

```text
schema_version
keyfile_group_id
source_folder_original_path
imported_keyfile_ids
eligible_file_count
min_keyfiles_per_set
max_keyfiles_per_set
combination_count_before_dedupe
duplicate_combination_count
final_combination_count
keyfile_set_ids
created_timestamp
warnings
notes
```

The app may also save a plain text preview for the user:

```text
generated/keyfile-lists/keyfile_combinations_<keyfile_group_id>_preview.txt
```

The plain text preview should list workspace-relative normalized paths only.

## Preview Before Saving

The Keyfile Builder should require preview before saving.

Preview should include:

```text
Selected target
Selected header
Selected mode set
Selected PIM set, if VeraCrypt applies
Keyfile mode
Keyfile group name
Keyfile group priority
Original selected files or folder
Eligible file count
Normalized workspace keyfile count
Large files capped to first 1 MiB
Optional full-copy import count
Optional thumbnail count
Generated keyfile set count before dedupe
Duplicate combinations skipped against earlier groups
Final new keyfile set count
Min keyfiles per set
Max keyfiles per set
Estimated job multiplication
Warnings
Output metadata paths
```

Example preview:

```text
Keyfile mode: folder combinations
Group: Photos small folder
Priority: 1
Eligible files: 12
Minimum keyfiles per set: 1
Maximum keyfiles per set: 2
Generated keyfile sets before dedupe: 78
Skipped duplicates from earlier groups: 0
Final new keyfile sets: 78
Large files capped to first 1 MiB: 2
Optional full copies imported: yes
Thumbnails generated: yes
Saved list: generated/keyfile-lists/keyfile_combinations_kfg_0001.json
```

## Validation Rules

The Keyfile Builder should validate before saving.

Required validation:

```text
selected files exist
selected files are readable
selected files are not folders
selected folder exists
selected folder is readable
folder scan found at least one eligible file for keyfile modes
workspace is writable
workspace normalized keyfile folder exists or can be created
workspace full-copy folder exists or can be created if enabled
workspace thumbnail folder exists or can be created if enabled
workspace manifest folder exists or can be created
min and max values are valid when generating combinations
generated combination count is not zero
all generated keyfile input paths are inside the workspace
all Hashcat job keyfile paths point to normalized workspace copies
```

Files that cannot be read should be skipped with a warning or block saving, depending on user choice.

Suggested warning:

```text
3 files could not be imported because they were unreadable. Continue with the remaining 9 files?
```

## Connecting Keyfile Sets to Job Drafts

The Keyfile Builder should update the job draft metadata.

A job draft should reference:

```text
keyfile_group_id
keyfile_mode
keyfile_set_ids
keyfile_set_count
keyfile_manifest_paths
generated_keyfile_list_path
normalized_keyfile_paths
optional_full_import_paths
optional_thumbnail_paths
```

The Keyfile Builder should not create final queue jobs by itself.

Final job expansion happens later after hash modes, PIMs, keyfiles, and password sources are combined.

## UI Behavior

Suggested Keyfile Builder screen:

```text
Keyfile Builder

Target:
  <target name>

Header:
  <header candidate>

Mode set:
  <mode set summary>

PIM set:
  <PIM summary, if applicable>

Keyfile group:
  Name: <group name>
  Priority: <order>

Keyfile options:
  [ ] No keyfiles
  [ ] Use selected keyfiles as one exact set
  [ ] Use all files in a folder as one keyfile set
  [ ] Generate combinations from files in a folder

Folder combination options:
  Minimum keyfiles per set: <number>
  Maximum keyfiles per set: <number>

Optional:
  [ ] Also include a no-keyfiles job variant
  [ ] Import full copies for browsing and thumbnails
  [ ] Generate workspace-local thumbnails for image keyfiles
  [ ] Skip combinations already covered by earlier keyfile groups

Buttons:
  Add Files
  Select Folder
  Preview Keyfile Sets
  Save Keyfile Group
  Move Group Up
  Move Group Down
  Clear
  Cancel
```

## Files Created or Modified

This step may create or modify:

```text
inputs/keyfiles/normalized/*
inputs/keyfiles/imported-full/*
inputs/keyfiles/thumbnails/*
inputs/keyfiles/manifests/keyfile_<keyfile_id>.json
generated/keyfile-lists/keyfile_combinations_<keyfile_group_id>.json
generated/keyfile-lists/keyfile_combinations_<keyfile_group_id>_preview.txt
generated/recipes/keyfile_set_<keyfile_set_id>.json
generated/recipes/keyfile_group_<keyfile_group_id>.json
jobs/drafts/job_<job_id>.json
jobs/command-previews/keyfiles_preview_<job_id>.txt
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
inputs/keyfiles/normalized/
inputs/keyfiles/imported-full/
inputs/keyfiles/thumbnails/
inputs/keyfiles/manifests/
generated/keyfile-lists/
generated/recipes/
jobs/drafts/
jobs/command-previews/
headers/metadata/
targets/
logs/app/
logs/errors/
cleanup/
temp/staging/
```

Temporary staging files must stay inside:

```text
temp/staging/
```

This step must not use:

```text
system temp folders
external folders by default
original volume files
original keyfile paths in final Hashcat jobs by default
operating system thumbnail caches
```

## App Behavior

The app should:

```text
load the selected target, header, hash mode set, and PIM set
allow no-keyfiles mode
allow exact selected keyfiles
allow importing selected keyfiles into the workspace
normalize all job keyfiles into inputs/keyfiles/normalized/
copy small keyfiles byte-for-byte exactly as-is
copy only the first 1,048,576 bytes from large keyfiles
allow optional full-copy import for browsing
allow optional workspace-local thumbnail generation for image keyfiles
allow selecting a folder and using eligible files as one keyfile set
allow selecting a folder and generating keyfile combinations
support multiple named keyfile groups
generate combinations, not permutations
treat keyfile order as not meaningful for job generation
validate min and max keyfile counts
warn about large keyfile set counts
allow priority ordering between groups
allow later groups to skip combinations already covered by earlier groups
never modify original keyfiles
never use original keyfile paths in final Hashcat jobs by default
save imported keyfile metadata
save keyfile group metadata
save keyfile set metadata
save generated keyfile lists
update job draft metadata
show preview before saving
save immediately after creating or changing a keyfile group or keyfile set
update the cleanup manifest
```

## Safety Rules

The Keyfile Builder must follow these rules:

```text
only support legitimate recovery of user-owned or authorized volumes
do not crack passwords itself
do not run Hashcat
do not modify original VeraCrypt or TrueCrypt volumes
do not modify original keyfiles
do not use original target files
work only from saved workspace target/header/job metadata
open original keyfiles read-only
normalize keyfiles into the workspace before job use
store normalized keyfiles inside the workspace
store optional full copies inside the workspace
store optional thumbnails inside the workspace
treat keyfiles and keyfile lists as sensitive recovery data
treat keyfile set metadata as forensic-trail data
do not print keyfile contents in logs, previews, reports, or errors
do not use system temp folders
do not use operating system thumbnail caches
do not save keyfile lists outside the workspace unless the user explicitly exports them later
do not upload, transmit, or exfiltrate keyfiles, keyfile lists, headers, metadata, jobs, logs, thumbnails, or results
do not claim secure deletion is guaranteed
describe cleanup as trace centralization and minimization
```

## Open Questions

Open questions for later steps:

```text
exact final job expansion logic when hash modes, PIMs, keyfiles, and password sources are combined
whether recursive folder scans should be included in version 1 or kept advanced
exact warning threshold for very large keyfile combination counts
whether to hard-block extremely large combination counts or only warn
exact report formatting for keyfile sets used in successful jobs
whether successful reports should show full keyfile names, keyfile IDs only, or both
whether thumbnail support should be limited to common image formats only
whether full-copy import should be disabled by default for very large files unless the user confirms
```

## Final Decisions

```text
The Keyfile Builder is Step 8.
The Keyfile Builder handles VeraCrypt and TrueCrypt keyfile choices.
The Keyfile Builder must not redesign hash mode selection, PIM handling, password building, queue running, or reports.
The app must support no keyfiles.
The app must support exact selected keyfiles.
The app must support importing keyfiles into the workspace.
The app must normalize keyfiles into workspace-local job keyfiles before use.
Original keyfiles are read-only sources.
Hashcat jobs must use normalized workspace keyfile copies by default.
Normalized keyfiles are stored in inputs/keyfiles/normalized/.
Small keyfiles are copied byte-for-byte exactly as-is.
Large keyfiles are copied byte-for-byte only up to the first 1,048,576 bytes.
Normalized keyfile data must not be compressed, encoded, padded, resized, hashed as replacement data, stripped, or otherwise transformed.
The app may optionally import full keyfile copies for browsing and thumbnail support.
Optional full copies are stored in inputs/keyfiles/imported-full/.
Optional full copies are not used in Hashcat jobs.
Optional thumbnails may be stored in inputs/keyfiles/thumbnails/.
Optional thumbnails must stay inside the workspace.
The app should support using all files in a folder as one keyfile set.
The app should support generating keyfile combinations from a folder.
The app must use combinations, not permutations.
Keyfile order should not create duplicate jobs.
Each final keyfile set becomes its own job option variant.
The app should validate min and max keyfiles per combination.
Minimum and maximum values must be positive integers.
Maximum must not exceed the number of eligible imported files.
The app should use a separate option if the user also wants a no-keyfiles variant.
The app should warn when generated keyfile set count is large.
The app should support multiple keyfile groups.
Keyfile groups may be ordered by likely priority.
Later groups may skip combinations already generated by earlier groups.
Deduplication across groups prevents duplicate job variants but must not alter the saved group definitions.
Deduplication should compare normalized keyfile content identity, not only filenames.
For VeraCrypt job variants, the command builder should use --veracrypt-keyfiles.
For TrueCrypt job variants, the command builder should use --truecrypt-keyfiles.
Hashcat keyfile paths should be passed as comma-separated workspace-local normalized file paths.
The app should store Hashcat arguments internally as argument arrays.
Command strings are only for preview or export.
The app should never modify original keyfiles.
The app should not use original keyfile paths in final Hashcat jobs by default.
The app should not pass a live folder path directly to Hashcat.
Folder imports should be saved as fixed snapshots inside the workspace.
Imported keyfile metadata should be stored in inputs/keyfiles/manifests/.
Generated keyfile lists should be stored in generated/keyfile-lists/.
Keyfile set and keyfile group recipes should be stored in generated/recipes/.
The Keyfile Builder should update job draft metadata but should not create final queue jobs by itself.
Final queue expansion happens later after hash modes, PIMs, keyfiles, and password sources are combined.
Keyfiles, keyfile lists, full copies, thumbnails, and keyfile set metadata should stay inside the workspace by default.
The app must not use system temp folders for keyfile data.
The app must not use operating system thumbnail caches for keyfile thumbnails.
The app must update the cleanup manifest for normalized keyfiles, optional full copies, optional thumbnails, generated keyfile lists, keyfile groups, and keyfile set metadata.
```

## Reference Notes

```text
Hashcat keyfile options confirmed:
--truecrypt-keyfiles
--veracrypt-keyfiles

Hashcat documentation:
https://hashcat.net/wiki/doku.php?id=hashcat

VeraCrypt notes confirmed:
VeraCrypt keyfiles are combined with the password.
Only the first 1,048,576 bytes of each keyfile are processed.
One or more keyfiles may be supplied.
VeraCrypt folder keyfile search paths remember the path, not filenames, so later folder changes can affect mounting behavior.

VeraCrypt keyfile documentation:
https://veracrypt.io/en/Keyfiles%20in%20VeraCrypt.html

TrueCrypt-compatible design note:
TrueCrypt keyfile behavior is treated the same way for this app: original keyfiles remain read-only, and Hashcat jobs use normalized workspace-local copies of the bytes relevant for keyfile processing.
```
