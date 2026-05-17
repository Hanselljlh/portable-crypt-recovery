# 05-header-extraction.md

## Purpose

This step defines how the app adds VeraCrypt and TrueCrypt volume sources and extracts job-ready headers into the workspace.

The app must keep this step focused on volume identity and header extraction only.

The app must not crack passwords itself.

The app must not run Hashcat against original full volumes.

The app must not modify original VeraCrypt or TrueCrypt volumes.

The app should open original volume sources read-only, extract selected 512-byte header candidates into the workspace, create normalized 512-byte job headers, save metadata, and connect those headers to later Hashcat jobs.

## Core Design Change

Header extraction should use a per-volume wizard.

The user should add and classify one volume source at a time instead of selecting many targets at once and trying to remember which settings belong to which target.

This keeps volume type, header type, and later job assumptions tied to the correct target.

Basic flow:

```text
Add Volume
→ Choose source type
→ Choose VeraCrypt, TrueCrypt, or Unknown
→ Choose what the volume is or may be
→ Choose valid header candidates
→ Review before extraction
→ Extract selected headers read-only
→ Save target and header records
→ Add another volume or return to Targets
```

The app can still support many volumes in one workspace.

Batch support should come from adding multiple saved volume records, not from forcing the user to configure many unrelated volumes on one screen.

## Add Volume Wizard

The Add Volume wizard should be the main way to add targets.

Suggested wizard pages:

```text
1. Select Source
2. Confirm Ownership
3. Choose Source Type
4. Choose Container Family
5. Choose Volume Possibility
6. Choose Header Candidates
7. Review Before Extraction
8. Extract and Save
9. Add Another Volume or Finish
```

### 1. Select Source

The user selects one source.

Supported source categories:

```text
File path
Physical device or partition path
Disk or drive image path
Already extracted header file
```

The app should not default to multi-select target adding in version 1.

The app may later add an advanced batch import mode, but the normal workflow should be one volume source at a time.

### 2. Confirm Ownership

The app should require confirmation that the user owns or is authorized to recover the selected volume source.

Suggested wording:

```text
Confirm that you own this volume or are authorized to recover it. The app will open the source read-only and will not modify the original volume.
```

The target should not be added or extracted until ownership or authorization is confirmed.

### 3. Choose Source Type

The user chooses what kind of source was selected.

Source type options:

```text
File container
Non-system partition/device
Non-system disk/drive image
System partition/drive/device
System disk/drive image
Already extracted header
Unknown / not sure
```

Use these meanings:

```text
File container
  A VeraCrypt or TrueCrypt container stored as a normal file.

Non-system partition/device
  A non-boot encrypted partition, USB drive, external drive, or device path.

Non-system disk/drive image
  A raw image or copied image of a non-system encrypted partition or device.

System partition/drive/device
  The original system-encrypted disk, drive, or device source.

System disk/drive image
  A raw image of a system-encrypted disk or drive.

Already extracted header
  A small header file already extracted by the user or another tool.

Unknown / not sure
  The user is unsure. The app should show safe candidate options and warnings.
```

### 4. Choose Container Family

The user chooses the likely container family.

Options:

```text
VeraCrypt
TrueCrypt
Unknown / decide later
```

Step 5 should record this value but should not try to build the final Hashcat mode yet.

Hash mode selection is handled in Step 6.

### 5. Choose Volume Possibility

The user chooses what the source is or may be.

For file containers:

```text
Standard file container
Hidden volume may exist
Unknown / try valid candidates
```

For non-system partition/device:

```text
Standard non-system volume
Hidden volume may exist
Unknown / try valid candidates
```

For non-system disk/drive image:

```text
Standard non-system volume image
Hidden volume may exist
Unknown / try valid candidates
```

For system partition/drive/device:

```text
Normal system encryption
Hidden operating system may exist
Unknown / try valid system candidates
```

For system disk/drive image:

```text
Normal system encryption image
Hidden operating system may exist
Unknown / try valid system candidates
```

For already extracted header:

```text
Normal / outer header candidate
Hidden volume header candidate
System header candidate
Unknown imported header
```

Important wording rule:

```text
Do not label a system source as simply "hidden volume."
For system encryption, use "hidden operating system" or "hidden system candidate."
```

A normal hidden volume and a hidden operating system are related concepts, but they should not be presented as the same checkbox.

## Actual Volume Creation Categories To Represent

The wizard should reflect the practical VeraCrypt and TrueCrypt creation categories:

```text
Encrypted file container
Encrypted non-system partition/drive/device
Encrypted system partition or entire system drive
Hidden volume inside a file container
Hidden volume inside a non-system partition/device-hosted volume
Hidden operating system / hidden system setup
```

Therefore, the app should not assume that only file containers can have hidden volumes.

Non-system partition/device-hosted volumes can also have hidden volumes.

System encryption should be handled separately as normal system encryption or hidden operating system possibility.

## Header Candidate Options

The app should show only valid or meaningful header candidate checkboxes for the selected source type.

### File Container

Allowed header candidates:

```text
Normal / outer volume header
Hidden volume header
```

Default:

```text
Normal / outer volume header: checked
Hidden volume header: unchecked
```

If the user chose “Hidden volume may exist” or “Unknown / try valid candidates”:

```text
Normal / outer volume header: checked
Hidden volume header: checked
```

### Non-System Partition/Device

Allowed header candidates:

```text
Normal / outer volume header
Hidden volume header
```

Default:

```text
Normal / outer volume header: checked
Hidden volume header: unchecked
```

If the user chose “Hidden volume may exist” or “Unknown / try valid candidates”:

```text
Normal / outer volume header: checked
Hidden volume header: checked
```

### Non-System Disk/Drive Image

Allowed header candidates:

```text
Normal / outer volume header
Hidden volume header
```

Default:

```text
Normal / outer volume header: checked
Hidden volume header: unchecked
```

If the user chose “Hidden volume may exist” or “Unknown / try valid candidates”:

```text
Normal / outer volume header: checked
Hidden volume header: checked
```

### System Partition/Drive/Device

Allowed header candidates:

```text
Normal system header
Hidden system / hidden OS candidate
```

Default:

```text
Normal system header: checked
Hidden system / hidden OS candidate: unchecked
```

If the user chose “Hidden operating system may exist” or “Unknown / try valid system candidates”:

```text
Normal system header: checked
Hidden system / hidden OS candidate: checked
```

The app should show a warning that system extraction must be from the correct disk, drive, device, or image start.

### System Disk/Drive Image

Allowed header candidates:

```text
Normal system header
Hidden system / hidden OS candidate
```

Default:

```text
Normal system header: checked
Hidden system / hidden OS candidate: unchecked
```

If the user chose “Hidden operating system may exist” or “Unknown / try valid system candidates”:

```text
Normal system header: checked
Hidden system / hidden OS candidate: checked
```

### Already Extracted Header

Allowed actions:

```text
Import as 512-byte normalized header
Import and normalize from file up to 128 KiB
Choose candidate role manually
```

Candidate role options:

```text
Normal / outer volume header
Hidden volume header
Normal system header
Hidden system / hidden OS candidate
Unknown imported header
```

The imported file rules from Step 2 still apply:

```text
If app-created: require exactly 512 bytes.
If user-imported: allow up to 128 KiB, then normalize/extract the needed 512-byte job header inside the workspace.
Reject files larger than 128 KiB.
```

## Header Extraction Offsets

The app should create one normalized 512-byte job header for each selected candidate.

### Normal / Outer Volume Header

Use for:

```text
File containers
Non-system partition/device sources
Non-system disk/drive images
```

Extraction rule:

```text
offset: 0
length: 512 bytes
```

### Hidden Volume Header

Use for:

```text
File containers where a hidden volume may exist
Non-system partition/device sources where a hidden volume may exist
Non-system disk/drive images where a hidden volume may exist
```

Extraction rule:

```text
offset: 65536
length: 512 bytes
```

### Normal System Header

Use for:

```text
System partition/drive/device sources
System disk/drive images
```

Extraction rule:

```text
offset: 31744
length: 512 bytes
```

The app should explain that this must be read from the correct disk, drive, device, or disk-image start.

### Hidden System / Hidden OS Candidate

Use only when the selected source may be part of a hidden operating system setup.

Version 1 should record this as a separate candidate type and show a clear warning.

The app should not treat it as the same thing as a normal hidden volume header.

For version 1, the app should avoid pretending it can fully detect or validate hidden operating system structure.

Suggested behavior:

```text
Allow the user to create a hidden system candidate record.
Require a warning.
Use the same strict read-only rules.
Store metadata clearly as hidden_system_candidate.
Let Step 6 and later job-building steps decide how to handle it.
```

If implementation needs to extract a 512-byte candidate immediately, it should use the system-header extraction path only when the selected source is the correct system disk, drive, device, or image.

## Review Before Extraction

Before writing any workspace header files, the app should show a review screen.

The review should display:

```text
Source path
Source type
Container family
Volume possibility
Ownership confirmed
Read-only check status
Selected header candidates
Offset and size for each selected candidate
Output filenames
Workspace path
Warnings
```

The user should confirm before extraction starts.

Suggested buttons:

```text
Back
Extract Headers
Cancel
```

## Read-Only Target Handling

The app should open original targets read-only.

For file sources, use binary read-only access.

For device, partition, disk, or image sources, use the safest read-only access supported by the operating system.

The app must not mount, repair, resize, write to, or otherwise modify original volumes.

The app must not copy full original target volumes into the workspace by default.

The app should store only the original path and target metadata.

If read-only access fails, the app should show a clear error and not extract anything.

Suggested error:

```text
The target could not be opened read-only. No header was extracted and the original target was not modified.
```

## Extraction Validation

Before extracting a candidate header, the app should check:

```text
target path exists
target is readable
target is opened read-only
target size is at least offset + 512 bytes
workspace is writable
required workspace folders exist
selected output path is inside the workspace
```

After extraction, the app should check:

```text
extracted file exists
extracted file is exactly 512 bytes
normalized job header exists
normalized job header is exactly 512 bytes
metadata was saved
cleanup manifest was updated
workspace state was saved
```

The app should not claim it can prove that a header is valid without the correct password.

Encrypted headers normally look random.

The app may warn about obvious extraction problems:

```text
source file too small
read returned fewer than 512 bytes
all-zero output
output path outside workspace
metadata save failed
workspace save failed
```

The app should not reject a candidate only because it cannot identify the encrypted header contents.

## Header Import

The user may import an already extracted header file.

Import rules:

```text
If imported file is exactly 512 bytes:
  copy it into headers/imported/
  create or copy a normalized 512-byte job header into headers/normalized/
  use the normalized 512-byte file for jobs

If imported file is larger than 512 bytes but no larger than 128 KiB:
  copy it into headers/imported/
  let the user choose candidate role manually
  extract or normalize the needed 512-byte job header into headers/normalized/

If imported file is larger than 128 KiB:
  reject it as too large for header import
```

The app should not run Hashcat against imported source header files directly unless they are normalized 512-byte job headers inside the workspace.

## Workspace Folders Used

This step uses these workspace folders:

```text
targets/
targets/target-notes/
targets/imported-target-metadata/

headers/
headers/imported/
headers/extracted/
headers/normalized/
headers/metadata/

jobs/drafts/

logs/app/
logs/errors/

cleanup/
temp/staging/
```

Temporary staging files must stay inside:

```text
temp/staging/
```

The app must not use the operating system temp folder for header extraction, imported headers, normalized headers, metadata, logs, or staging files.

## Files Created or Modified

This step may create or modify:

```text
targets/targets.json
targets/target-notes/*
targets/imported-target-metadata/*

headers/imported/*
headers/extracted/*
headers/normalized/*
headers/metadata/*

jobs/drafts/*

logs/app/*
logs/errors/*

cleanup/cleanup-manifest.json
workspace.json
settings.json
```

Suggested extracted header filename pattern:

```text
headers/extracted/target_<target_id>_<candidate_type>_offset_<offset>_raw512.bin
```

Suggested normalized header filename pattern:

```text
headers/normalized/target_<target_id>_<candidate_type>_job_header_512.bin
```

Suggested metadata filename pattern:

```text
headers/metadata/header_<header_id>.json
```

Examples:

```text
headers/extracted/target_t0001_normal_volume_offset_0_raw512.bin
headers/extracted/target_t0001_hidden_volume_offset_65536_raw512.bin
headers/extracted/target_t0002_normal_system_offset_31744_raw512.bin

headers/normalized/target_t0001_normal_volume_job_header_512.bin
headers/normalized/target_t0001_hidden_volume_job_header_512.bin
headers/normalized/target_t0002_normal_system_job_header_512.bin

headers/metadata/header_h0001.json
headers/metadata/header_h0002.json
headers/metadata/header_h0003.json
```

## Header Metadata

Each extracted or imported header should have a metadata record.

Suggested fields:

```text
header_id
target_id
source_type
source_category
container_family
volume_possibility
candidate_type
source_original_path
source_workspace_path
extracted_header_path
normalized_header_path
source_offset
extracted_size
normalized_size
source_file_size
source_modified_timestamp
extraction_timestamp
sha256_extracted_header
sha256_normalized_header
validation_status
job_ready
cracked_status
successful_job_id
successful_run_id
cracked_result_path
possible_encryption_algorithms
possible_hash_algorithms
pim_status
keyfile_status
password_strategy_status
notes
```

Suggested values for `source_type`:

```text
app_extracted
user_imported
```

Suggested values for `source_category`:

```text
file_container
non_system_partition_device
non_system_disk_image
system_partition_drive_device
system_disk_image
already_extracted_header
unknown
```

Suggested values for `container_family`:

```text
veracrypt
truecrypt
unknown
```

Suggested values for `volume_possibility`:

```text
standard_volume
hidden_volume_may_exist
normal_system_encryption
hidden_operating_system_may_exist
unknown
```

Suggested values for `candidate_type`:

```text
normal_volume_header
hidden_volume_header
normal_system_header
hidden_system_candidate
unknown_imported_header
```

The fields below are placeholders for later steps and should not be filled with detailed user choices in Step 5 unless the user volunteers the information:

```text
possible_encryption_algorithms
possible_hash_algorithms
pim_status
keyfile_status
password_strategy_status
```

Hash mode selection is handled in Step 6.

PIM handling is handled in Step 7.

Keyfile handling is handled in Step 8.

Password strategy is handled in Step 9.

## Target Metadata

Each volume source should have a record in:

```text
targets/targets.json
```

Suggested fields:

```text
target_id
display_name
original_path
source_category
container_family
volume_possibility
ownership_confirmed
source_file_size
source_modified_timestamp
added_timestamp
header_extraction_status
header_ids
normalized_header_ids
cracked_status
successful_header_id
successful_job_id
possible_encryption_algorithms
possible_hash_algorithms
pim_status
keyfile_status
password_strategy_status
notes
```

The target record should not store:

```text
passwords
candidate passwords
keyfile contents
potfile data
cracked results
```

## Connecting Headers to Later Hashcat Jobs

Later job-building steps should use only normalized 512-byte job headers from:

```text
headers/normalized/
```

A job should reference:

```text
target_id
header_id
normalized_header_path
container_family
source_category
volume_possibility
candidate_type
```

The job builder must not use the original target path as Hashcat input.

The job builder should use the per-volume metadata so the user does not need to remember which settings belonged to which volume.

This is especially important for later steps where each volume/header may have different:

```text
possible encryption algorithms
possible hash algorithms
PIM assumptions
keyfile assumptions
password strategy
```

## UI Behavior

The Targets screen should show each volume source with its extracted headers underneath.

Example:

```text
Target: backup_drive.tc
Family: VeraCrypt
Source: File container
Possibility: Hidden volume may exist
Original path: D:/backup_drive.tc

Headers:
  - normal_volume_header, 512 bytes, job-ready
  - hidden_volume_header, 512 bytes, job-ready

Status: not cracked
```

Example system source:

```text
Target: laptop_disk_image.dd
Family: TrueCrypt
Source: System disk image
Possibility: Normal system encryption

Headers:
  - normal_system_header, 512 bytes, job-ready

Status: not cracked
```

Suggested target actions:

```text
Add Volume
Add Another Volume
Extract More Headers
Import Header For This Target
Create Job From Header
View Header Metadata
Remove Target
```

Suggested header actions:

```text
Create Job From This Header
Show File Location
View Metadata
Mark As Not Job-Ready
Remove Header From Workspace
```

Removing a target or header from the workspace must not delete or modify the original volume.

If the app deletes workspace-created extracted headers, it should treat that as normal deletion and update the cleanup manifest.

The app must not claim secure deletion.

## Warnings

### System Header Warning

Suggested wording:

```text
System header extraction should be used only when the selected source starts at the correct disk, drive, device, or disk-image beginning. If you select the wrong partition, mounted volume, or image, the extracted 512 bytes may not work. The app will read only 512 bytes and will not modify the source.
```

### Hidden Volume Warning

Suggested wording:

```text
A hidden volume header candidate can be extracted, but the app cannot confirm that a hidden volume exists without the correct password. Hidden header areas are designed to look like random data.
```

### Hidden Operating System Warning

Suggested wording:

```text
A hidden operating system is not the same as a normal hidden volume. Use this option only if the selected source may be part of a hidden operating system setup. The app cannot prove that a hidden operating system exists from the header bytes alone.
```

### Unknown Source Warning

Suggested wording:

```text
Unknown mode may create more than one header candidate for this source. Later steps may create separate Hashcat jobs for each candidate. This can increase queue size, but it prevents guessing too early.
```

## Backup Header Note

VeraCrypt and TrueCrypt support embedded backup headers near the end of non-system volumes.

For version 1, backup header extraction should not be part of the main simple workflow unless the user asks for it later.

The metadata schema should still keep enough information to add backup header candidates later:

```text
source_offset
candidate_type
source_file_size
volume_possibility
```

## App Behavior

The app should:

```text
use a per-volume Add Volume wizard
add one volume source at a time
allow repeated Add Another Volume flow
require ownership or authorization confirmation per volume source
open original sources read-only
never modify original sources
never copy full original volumes into the workspace by default
record original source path and metadata only
show only valid header candidate checkboxes for the chosen source type
support file container sources
support non-system partition/device sources
support non-system disk/drive image sources
support system partition/drive/device sources
support system disk/drive image sources
support already extracted header imports
support unknown source mode
extract selected 512-byte header candidates
create one normalized 512-byte job header per selected candidate
store extracted headers inside the workspace
store normalized job headers inside the workspace
store header metadata inside the workspace
store target metadata inside the workspace
connect normalized headers to later job creation
save immediately after target add, header extraction, header import, and metadata changes
auto-save as already decided in earlier steps
log errors without exposing secrets
update the cleanup manifest
```

## Safety Rules

The app must follow these rules:

```text
only support legitimate recovery of user-owned or authorized volumes
require user confirmation before adding a volume source
never modify original VeraCrypt or TrueCrypt volumes
open original sources read-only
never run Hashcat against original full volumes
never use original target files as Hashcat job input
only use normalized 512-byte workspace headers as Hashcat job input
store extracted headers inside the workspace
store normalized headers inside the workspace
store imported headers inside the workspace
store metadata inside the workspace
do not use system temp folders for header data
do not upload, transmit, or exfiltrate targets, headers, metadata, logs, or results
do not claim secure deletion is guaranteed
describe cleanup as trace centralization and minimization
warn when system extraction may be using the wrong source
warn that hidden volume headers cannot be identified without the correct password
warn that hidden operating system handling is separate from normal hidden volume handling
```

## Open Questions

Open questions for later steps:

```text
whether to add advanced embedded backup header extraction
exact UI layout for physical disk and partition selection
exact Windows raw device read-only behavior
exact Linux raw device permission handling
exact final JSON schema for target records
exact final JSON schema for header metadata records
whether duplicate header checks should block or only warn
how much original target fingerprinting should be done without hashing large files
exact handling for hidden operating system candidates
whether an advanced batch import wizard should be added after version 1
```

## Final Decisions

```text
The app uses a per-volume Add Volume wizard for header extraction.
The normal workflow adds one volume source at a time.
The user can add another volume after each volume is processed.
Batch support means the workspace can contain many volume records, not that the first version needs multi-volume selection in one wizard.
The app supports file containers.
The app supports non-system partition/device sources.
The app supports non-system disk/drive image sources.
The app supports system partition/drive/device sources.
The app supports system disk/drive image sources.
The app supports already extracted header imports.
The app supports Unknown / not sure mode.
The app should reflect actual VeraCrypt and TrueCrypt creation categories.
File containers can be standard or may contain a hidden volume.
Non-system partition/device-hosted volumes can be standard or may contain a hidden volume.
System encryption should be handled as normal system encryption or hidden operating system possibility.
A normal hidden volume and a hidden operating system should not be presented as the same checkbox.
The app must require ownership or authorization confirmation before extraction.
The app opens original sources read-only.
The app never modifies original target volumes.
The app does not copy full target volumes into the workspace by default.
The app stores original source path and metadata only.
The app extracts headers into the workspace.
The app creates normalized 512-byte job headers inside the workspace.
The app-created job header size is exactly 512 bytes.
Normal / outer volume header extraction uses offset 0 and length 512 bytes.
Hidden volume header extraction uses offset 65536 and length 512 bytes.
Normal system header extraction uses offset 31744 and length 512 bytes.
Hidden system / hidden OS candidate is a separate candidate type.
System header extraction should warn the user about selecting the correct disk, drive, device, or image source.
Unknown mode is a guided checkbox workflow, not a separate real header type.
Unknown mode may extract multiple valid candidate headers from the same source.
Each selected header candidate becomes a separate extracted header record.
Each extracted candidate gets its own normalized 512-byte job header.
Each normalized header can later generate separate Hashcat jobs.
The job builder must use normalized headers from headers/normalized/.
The job builder must not use original target files as Hashcat input.
The app should support importing already extracted headers.
Imported headers larger than 128 KiB are rejected.
Imported headers are copied into the workspace before normalization.
Header metadata is saved in headers/metadata/.
Target metadata is saved in targets/targets.json.
The cleanup manifest is updated for extracted, imported, and normalized headers.
The app should save immediately after adding targets, extracting headers, importing headers, and changing header metadata.
The app should not claim it can prove a header is valid without the correct password.
The app should warn that hidden volume headers are designed to look random.
The app should warn that hidden operating system handling is separate from normal hidden volume handling.
Backup header extraction is not part of the simple version 1 workflow unless added later.
The metadata schema should keep source_offset, candidate_type, source_file_size, and volume_possibility so backup extraction can be added later.
The target and header metadata should include placeholders for possible encryption algorithms, possible hash algorithms, PIM status, keyfile status, and password strategy status.
Step 5 records those placeholders but does not redesign Step 6, Step 7, Step 8, or Step 9.
```

## Reference Notes

These references were used to confirm the high-level distinctions and header extraction assumptions for this step:

```text
Hashcat FAQ and forum guidance for TrueCrypt/VeraCrypt header extraction:
- system/boot header candidate: 512 bytes at offset 31744
- hidden partition/volume candidate: 512 bytes at offset 65536
- non-boot file/non-system partition candidate: first 512 bytes

VeraCrypt documentation:
- hidden volumes can be created inside file-hosted or partition/device-hosted volumes
- hidden operating system is a separate system-encryption feature

TrueCrypt documentation:
- supports file containers, non-system partition/device encryption, system encryption, hidden volumes, and hidden operating systems
```
