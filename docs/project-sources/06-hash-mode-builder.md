# 06-hash-mode-builder.md

## Purpose

This step defines how the app builds VeraCrypt and TrueCrypt Hashcat mode choices.

The hash mode builder does not crack passwords, extract headers, build password lists, handle keyfiles, handle PIM expansion, run Hashcat, or manage the queue.

Its job is to take one normalized workspace header from Step 5 and create one or more valid Hashcat mode entries for that header.

The builder should help the user describe what the volume may be, then generate only the Hashcat modes that are valid for:

```text
container family
source / volume type
header candidate type
encryption algorithm family
hash / PRF / KDF choice
installed Hashcat support
workspace safety rules
```

The app should support a simple broad option for users who do not know the details:

```text
I only know this is a VeraCrypt or TrueCrypt volume. Try every valid supported mode for this header.
```

This option should expand to valid VeraCrypt and TrueCrypt mode choices for the selected normalized header, then skip invalid or unsupported combinations.

## Core Scope

Step 6 handles:

```text
VeraCrypt / TrueCrypt family selection
volume/source type review
normal / hidden / system / hidden-system header role
encryption algorithm assumptions
hash / PRF / KDF assumptions
OR-style mode entries
try-everything-valid mode expansion
mapping to Hashcat -m mode numbers
invalid-combination filtering
installed-Hashcat support checking
manual Hashcat mode override
mode preview before jobs are generated
mode-set storage in the workspace
```

Step 6 does not handle:

```text
header extraction
PIM expansion
keyfile expansion
password strategy generation
final queue job expansion
Hashcat process running
reports
```

## Important Design Rule

The app cannot reliably detect the true encryption algorithm, PRF, KDF, hidden status, or container family from encrypted header bytes alone.

The hash mode builder should present choices as:

```text
Known or possible assumptions to try
```

not as:

```text
Detected settings
```

If the user does not know the details, the app should make it easy to use broad choices without pretending to know more than it does.

## User Inputs

The Hash Mode Builder screen should accept:

```text
Selected target
Selected normalized 512-byte workspace header
Container family
Source / volume type from Step 5 metadata
Header candidate type from Step 5 metadata
Encryption algorithm choice
Hash / PRF / KDF choice
OR-style mode entries
Try-everything-valid option
Manual Hashcat -m override
```

## Container Family Choices

The app should show:

```text
VeraCrypt
TrueCrypt
Both / Unknown
```

### VeraCrypt

Only VeraCrypt-valid encryption algorithms and PRF/KDF options should be selectable.

TrueCrypt-only choices should be hidden, disabled, or marked invalid with a clear reason.

### TrueCrypt

Only TrueCrypt-valid encryption algorithms and hash/PRF options should be selectable.

VeraCrypt-only choices should be hidden, disabled, or marked invalid with a clear reason.

### Both / Unknown

The app should expand to both VeraCrypt and TrueCrypt possibilities, but only valid combinations should be generated.

The app should not generate combinations such as:

```text
TrueCrypt + SHA-256
TrueCrypt + Streebog
TrueCrypt + BLAKE2s
TrueCrypt + Argon2id
TrueCrypt + Camellia
TrueCrypt + Kuznyechik
```

because those are not TrueCrypt choices.

## Try-Everything-Valid Option

The app should include a broad beginner-safe option:

```text
I only know this is a VeraCrypt or TrueCrypt volume. Try every valid supported mode for this header.
```

Suggested UI label:

```text
Try Every Valid VeraCrypt / TrueCrypt Mode
```

Expected behavior:

```text
family = Both / Unknown
volume/header type = inferred from selected header metadata when possible
encryption = all valid family-specific choices
hash / PRF / KDF = all valid family-specific choices
mode support = installed Hashcat modes only by default
invalid combinations = skipped with reasons
duplicates = removed
preview = required before job drafts are generated
```

This option should not mean:

```text
try every password
try every PIM
try every keyfile
try every wordlist
run anything immediately
```

It only expands hash mode assumptions.

If the selected header metadata is unknown, the app should ask whether to try:

```text
non-system modes only
system / boot modes only
both non-system and system / boot modes
```

If the header came from a Step 5 normal or hidden non-system candidate, default to non-system modes.

If the header came from a Step 5 system or hidden-system candidate, default to system / boot modes.

## Source / Volume Types To Represent

The hash mode builder should display the source / volume type from Step 5 so the user can verify what they are building against.

The app should explicitly represent all of these cases:

```text
File container, normal / outer volume
File container, hidden volume may exist

Non-system partition/device, normal / outer volume
Non-system partition/device, hidden volume may exist

Non-system disk/drive image, normal / outer volume
Non-system disk/drive image, hidden volume may exist

System partition/drive/device, normal system encryption
System partition/drive/device, hidden system / hidden OS may exist

System disk/drive image, normal system encryption
System disk/drive image, hidden system / hidden OS may exist

Already extracted header, manually assigned role
Unknown / not sure
```

The builder should not collapse these into only “normal,” “hidden,” and “system.”

The source type matters for warnings, preview wording, and avoiding user confusion.

## Header Candidate Types

The builder should use the Step 5 header candidate type as the default mode category.

Supported header candidate types:

```text
normal_volume_header
hidden_volume_header
normal_system_header
hidden_system_candidate
unknown_imported_header
```

### Normal Volume Header

Use non-system modes.

Applies to:

```text
file container normal header
non-system partition/device normal header
non-system disk/image normal header
```

### Hidden Volume Header

Use non-system modes.

Applies to:

```text
file container hidden header
non-system partition/device hidden header
non-system disk/image hidden header
```

Important:

```text
Normal and hidden non-system headers use the same Hashcat mode families.
The difference is the extracted header candidate, not the -m number.
```

### Normal System Header

Use system / boot modes.

Applies to:

```text
system partition/drive/device normal system header
system disk/drive image normal system header
```

### Hidden System Candidate

Use system / boot modes.

Important:

```text
A hidden system / hidden OS candidate is not the same thing as a normal hidden volume header.
Do not present it as a normal hidden volume.
```

### Unknown Imported Header

The app should ask the user to assign a role:

```text
Normal / outer volume header
Hidden volume header
Normal system header
Hidden system / hidden OS candidate
Unknown, try valid role groups
```

If the user chooses “Unknown, try valid role groups,” the app may expand both non-system and system / boot modes, but it must clearly warn that this increases the number of jobs.

## Encryption Algorithm Choices

The app should keep algorithm selection family-specific.

### TrueCrypt Encryption Choices

TrueCrypt choices:

```text
AES
Serpent
Twofish
AES-Twofish
AES-Twofish-Serpent
Serpent-AES
Serpent-Twofish-AES
Twofish-Serpent
Unknown / all TrueCrypt-supported encryption choices
```

### VeraCrypt Encryption Choices

VeraCrypt choices should include current and legacy VeraCrypt-supported choices:

```text
AES
Camellia
Kuznyechik
Serpent
Twofish
AES-Twofish
AES-Twofish-Serpent
Camellia-Kuznyechik
Camellia-Serpent
Kuznyechik-AES
Kuznyechik-Serpent-Camellia
Kuznyechik-Twofish
Serpent-AES
Serpent-Twofish-AES
Twofish-Serpent
GOST89 legacy, if supported by the compatibility table
Unknown / all VeraCrypt-supported encryption choices
```

The app should not let the user pick VeraCrypt-only encryption choices when the family is set to TrueCrypt.

Examples of VeraCrypt-only choices:

```text
Camellia
Kuznyechik
Camellia-Kuznyechik
Camellia-Serpent
Kuznyechik-AES
Kuznyechik-Serpent-Camellia
Kuznyechik-Twofish
GOST89 legacy
```

## Cipher Group Mapping

Hashcat TrueCrypt and VeraCrypt modes generally group encryption by XTS key size, not by every individual cipher name.

The app should map selected encryption choices into cipher groups:

```text
XTS 512-bit group:
  single cipher

XTS 1024-bit group:
  two-cipher cascade

XTS 1536-bit group:
  three-cipher cascade
```

Examples:

```text
AES → XTS 512-bit group
Serpent → XTS 512-bit group
Twofish → XTS 512-bit group
Camellia → XTS 512-bit group
Kuznyechik → XTS 512-bit group

AES-Twofish → XTS 1024-bit group
Serpent-AES → XTS 1024-bit group
Twofish-Serpent → XTS 1024-bit group
Camellia-Kuznyechik → XTS 1024-bit group
Kuznyechik-AES → XTS 1024-bit group
Kuznyechik-Twofish → XTS 1024-bit group
Camellia-Serpent → XTS 1024-bit group

AES-Twofish-Serpent → XTS 1536-bit group
Serpent-Twofish-AES → XTS 1536-bit group
Kuznyechik-Serpent-Camellia → XTS 1536-bit group
```

If multiple selected encryption algorithms map to the same family, PRF/KDF, boot category, and XTS group, the app should deduplicate the resulting Hashcat modes.

Example:

```text
Selected:
  AES
  Serpent
  Twofish

Generated:
  one XTS 512-bit mode for the chosen family and PRF/KDF
```

The preview should explain why the duplicates collapsed.

## Hash / PRF / KDF Choices

The app should separate TrueCrypt, VeraCrypt PBKDF2-HMAC, and VeraCrypt Argon2id behavior.

### TrueCrypt Hash / PRF Choices

TrueCrypt choices:

```text
PBKDF2-HMAC-RIPEMD160
PBKDF2-HMAC-SHA512
PBKDF2-HMAC-Whirlpool
Unknown / all TrueCrypt-supported hash choices
```

TrueCrypt should not allow:

```text
SHA-256
Streebog-512
BLAKE2s-256
Argon2id
```

### VeraCrypt PBKDF2-HMAC PRF Choices

VeraCrypt choices:

```text
PBKDF2-HMAC-RIPEMD160 legacy
PBKDF2-HMAC-SHA512
PBKDF2-HMAC-Whirlpool
PBKDF2-HMAC-SHA256
PBKDF2-HMAC-Streebog-512
PBKDF2-HMAC-BLAKE2s-256
Unknown / all VeraCrypt-supported PBKDF2-HMAC choices
```

### VeraCrypt Argon2id KDF Choice

VeraCrypt Argon2id should be represented separately from hash/PRF selection.

Suggested UI:

```text
KDF:
  PBKDF2-HMAC
  Argon2id
  Unknown / all VeraCrypt-supported KDF choices
```

If Argon2id is selected:

```text
do not show a separate hash selection
show that Argon2id uses its own internal BLAKE2b hash
require PIM handling in Step 7
check installed Hashcat support before generating modes
skip if no supported Hashcat mode exists
```

If no installed Hashcat mode supports VeraCrypt Argon2id, the preview should show:

```text
Skipped: valid VeraCrypt KDF choice, but this Hashcat build does not report a supported VeraCrypt Argon2id mode.
```

## Family, Algorithm, and Version Compatibility Validation

The app should perform two separate validations.

### 1. Valid For VeraCrypt / TrueCrypt

This checks whether a selected algorithm belongs to the selected container family.

Examples:

```text
TrueCrypt + AES:
  valid

TrueCrypt + Camellia:
  invalid, VeraCrypt-only encryption option

TrueCrypt + SHA-256:
  invalid, VeraCrypt-only PRF option

VeraCrypt + Kuznyechik:
  valid for VeraCrypt, but may be version-dependent

VeraCrypt + RIPEMD160:
  valid only as legacy VeraCrypt compatibility

VeraCrypt + GOST89:
  legacy VeraCrypt compatibility only, removed from modern VeraCrypt mounting support
```

### 2. Supported By Installed Hashcat

This checks whether the installed Hashcat executable reports a compatible mode.

The app should keep a built-in compatibility table, but the installed Hashcat support check should be treated as the practical source for job generation.

Suggested status values:

```text
supported_by_installed_hashcat
not_supported_by_installed_hashcat
supported_by_legacy_mode_only
supported_by_current_mode
manual_override_only
unknown_support
```

If a combination is valid for VeraCrypt/TrueCrypt but unsupported by the installed Hashcat build, the app should not silently remove it.

The preview should show:

```text
Valid container option, but unsupported by this Hashcat build.
```

## Installed Hashcat Mode Check

After Hashcat is verified in Step 3, the app should parse or query the installed Hashcat mode list.

Suggested implementation behavior:

```text
run Hashcat help or mode-list output as an argument array
capture supported mode numbers and names
cache the result in workspace settings
refresh when the Hashcat path or version changes
use the detected list to mark supported and unsupported modes
```

The exact command can be finalized during implementation.

The app should not rely only on hard-coded assumptions because Hashcat modes can be added, removed, renamed, superseded, or marked legacy.

The built-in table is for:

```text
UI explanations
offline preview
initial defaults
manual override validation
clear skip reasons
```

The installed Hashcat mode list is for:

```text
whether this workspace can actually generate runnable jobs for those modes
```

## Hashcat Input Format Awareness

The mode builder should record the required Hashcat input format for each selected mode.

Possible input formats:

```text
normalized_512_byte_header_file
converted_truecrypt_hash_string_file
converted_veracrypt_hash_string_file
unknown_manual_override
```

The normalized 512-byte workspace header remains the trusted source from Step 5.

If a current Hashcat mode requires a `$truecrypt$` or `$veracrypt$` text input instead of a raw 512-byte header file, the later command builder should create that derived input inside the workspace from the normalized header.

Suggested derived-input folder:

```text
generated/commands/
```

or, if implementation prefers a dedicated folder later:

```text
generated/hash-inputs/
```

Rules:

```text
do not read original volumes for conversion
read only the normalized workspace header
write derived Hashcat input inside the workspace
track it in the cleanup manifest
treat it as forensic-trail project data
do not use system temp folders
```

Step 6 should only record this requirement. The final command builder can decide the exact converter call or internal conversion method later.

## Current Hashcat Mode Mapping

The app should prefer current Hashcat modes when supported.

Current mode groups use generalized TrueCrypt/VeraCrypt hash strings and XTS groups.

### Current TrueCrypt Non-System Modes

Use for:

```text
normal_volume_header
hidden_volume_header
```

```text
29311  TrueCrypt RIPEMD160 + XTS 512 bit
29312  TrueCrypt RIPEMD160 + XTS 1024 bit
29313  TrueCrypt RIPEMD160 + XTS 1536 bit

29321  TrueCrypt SHA512 + XTS 512 bit
29322  TrueCrypt SHA512 + XTS 1024 bit
29323  TrueCrypt SHA512 + XTS 1536 bit

29331  TrueCrypt Whirlpool + XTS 512 bit
29332  TrueCrypt Whirlpool + XTS 1024 bit
29333  TrueCrypt Whirlpool + XTS 1536 bit
```

### Current TrueCrypt System / Boot Modes

Use for:

```text
normal_system_header
hidden_system_candidate
```

```text
29341  TrueCrypt RIPEMD160 + XTS 512 bit + boot-mode
29342  TrueCrypt RIPEMD160 + XTS 1024 bit + boot-mode
29343  TrueCrypt RIPEMD160 + XTS 1536 bit + boot-mode
```

TrueCrypt SHA512 boot and Whirlpool boot should be treated as unsupported unless the installed Hashcat build reports valid modes.

### Current VeraCrypt Non-System Modes

Use for:

```text
normal_volume_header
hidden_volume_header
```

```text
29411  VeraCrypt RIPEMD160 + XTS 512 bit
29412  VeraCrypt RIPEMD160 + XTS 1024 bit
29413  VeraCrypt RIPEMD160 + XTS 1536 bit

29421  VeraCrypt SHA512 + XTS 512 bit
29422  VeraCrypt SHA512 + XTS 1024 bit
29423  VeraCrypt SHA512 + XTS 1536 bit

29431  VeraCrypt Whirlpool + XTS 512 bit
29432  VeraCrypt Whirlpool + XTS 1024 bit
29433  VeraCrypt Whirlpool + XTS 1536 bit

29451  VeraCrypt SHA256 + XTS 512 bit
29452  VeraCrypt SHA256 + XTS 1024 bit
29453  VeraCrypt SHA256 + XTS 1536 bit

29471  VeraCrypt Streebog-512 + XTS 512 bit
29472  VeraCrypt Streebog-512 + XTS 1024 bit
29473  VeraCrypt Streebog-512 + XTS 1536 bit
```

### Current VeraCrypt System / Boot Modes

Use for:

```text
normal_system_header
hidden_system_candidate
```

```text
29441  VeraCrypt RIPEMD160 + XTS 512 bit + boot-mode
29442  VeraCrypt RIPEMD160 + XTS 1024 bit + boot-mode
29443  VeraCrypt RIPEMD160 + XTS 1536 bit + boot-mode

29461  VeraCrypt SHA256 + XTS 512 bit + boot-mode
29462  VeraCrypt SHA256 + XTS 1024 bit + boot-mode
29463  VeraCrypt SHA256 + XTS 1536 bit + boot-mode

29481  VeraCrypt Streebog-512 + XTS 512 bit + boot-mode
29482  VeraCrypt Streebog-512 + XTS 1024 bit + boot-mode
29483  VeraCrypt Streebog-512 + XTS 1536 bit + boot-mode
```

VeraCrypt SHA512 boot, Whirlpool boot, BLAKE2s-256, and Argon2id should be treated as unsupported by the built-in mode map unless the installed Hashcat build reports valid supported modes.

## Legacy Hashcat Mode Mapping

The app may keep legacy modes for older Hashcat builds or manual override support.

Legacy mode groups are useful when the installed Hashcat version still reports them.

### Legacy TrueCrypt Non-System Modes

```text
6211  TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + XTS 512-bit group
6212  TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + XTS 1024-bit group
6213  TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + XTS 1536-bit group

6221  TrueCrypt 5.0+ PBKDF2-HMAC-SHA512 + XTS 512-bit group
6222  TrueCrypt 5.0+ PBKDF2-HMAC-SHA512 + XTS 1024-bit group
6223  TrueCrypt 5.0+ PBKDF2-HMAC-SHA512 + XTS 1536-bit group

6231  TrueCrypt 5.0+ PBKDF2-HMAC-Whirlpool + XTS 512-bit group
6232  TrueCrypt 5.0+ PBKDF2-HMAC-Whirlpool + XTS 1024-bit group
6233  TrueCrypt 5.0+ PBKDF2-HMAC-Whirlpool + XTS 1536-bit group
```

### Legacy TrueCrypt System / Boot Modes

```text
6241  TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + XTS 512-bit group + boot-mode
6242  TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + XTS 1024-bit group + boot-mode
6243  TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + XTS 1536-bit group + boot-mode
```

### Legacy VeraCrypt Non-System Modes

```text
13711  VeraCrypt PBKDF2-HMAC-RIPEMD160 + XTS 512-bit group
13712  VeraCrypt PBKDF2-HMAC-RIPEMD160 + XTS 1024-bit group
13713  VeraCrypt PBKDF2-HMAC-RIPEMD160 + XTS 1536-bit group

13721  VeraCrypt PBKDF2-HMAC-SHA512 + XTS 512-bit group
13722  VeraCrypt PBKDF2-HMAC-SHA512 + XTS 1024-bit group
13723  VeraCrypt PBKDF2-HMAC-SHA512 + XTS 1536-bit group

13731  VeraCrypt PBKDF2-HMAC-Whirlpool + XTS 512-bit group
13732  VeraCrypt PBKDF2-HMAC-Whirlpool + XTS 1024-bit group
13733  VeraCrypt PBKDF2-HMAC-Whirlpool + XTS 1536-bit group

13751  VeraCrypt PBKDF2-HMAC-SHA256 + XTS 512-bit group
13752  VeraCrypt PBKDF2-HMAC-SHA256 + XTS 1024-bit group
13753  VeraCrypt PBKDF2-HMAC-SHA256 + XTS 1536-bit group

13771  VeraCrypt PBKDF2-HMAC-Streebog-512 + XTS 512-bit group
13772  VeraCrypt PBKDF2-HMAC-Streebog-512 + XTS 1024-bit group
13773  VeraCrypt PBKDF2-HMAC-Streebog-512 + XTS 1536-bit group
```

### Legacy VeraCrypt System / Boot Modes

```text
13741  VeraCrypt PBKDF2-HMAC-RIPEMD160 + XTS 512-bit group + boot-mode
13742  VeraCrypt PBKDF2-HMAC-RIPEMD160 + XTS 1024-bit group + boot-mode
13743  VeraCrypt PBKDF2-HMAC-RIPEMD160 + XTS 1536-bit group + boot-mode

13761  VeraCrypt PBKDF2-HMAC-SHA256 + XTS 512-bit group + boot-mode
13762  VeraCrypt PBKDF2-HMAC-SHA256 + XTS 1024-bit group + boot-mode
13763  VeraCrypt PBKDF2-HMAC-SHA256 + XTS 1536-bit group + boot-mode

13781  VeraCrypt PBKDF2-HMAC-Streebog-512 + XTS 512-bit group + boot-mode
13782  VeraCrypt PBKDF2-HMAC-Streebog-512 + XTS 1024-bit group + boot-mode
13783  VeraCrypt PBKDF2-HMAC-Streebog-512 + XTS 1536-bit group + boot-mode
```

## Mode Preference Rule

When both current and legacy modes are supported by the installed Hashcat build, the app should prefer current modes.

Suggested priority:

```text
1. Current supported mode
2. Legacy supported mode
3. Manual override with warning
4. Unsupported, skipped with reason
```

The app should record whether a mode is:

```text
current
legacy
manual_override
unsupported
```

## OR-Style Mode Entries

The user should be able to create multiple mode entries and combine them with OR logic.

Example:

```text
Entry 1:
  VeraCrypt
  File container / normal header
  AES
  SHA-512

OR Entry 2:
  VeraCrypt
  File container / hidden header
  AES
  SHA-512

OR Entry 3:
  TrueCrypt
  Non-system partition/device / normal header
  AES-Twofish-Serpent
  RIPEMD-160

OR Entry 4:
  Both / Unknown
  Try every valid supported mode for this header
```

The app should store the original entries and the expanded results.

The preview should show:

```text
entry selected by user
expanded family
expanded source/header type
expanded encryption
expanded XTS group
expanded hash / PRF / KDF
mapped Hashcat mode
current or legacy
supported by installed Hashcat
skip reason, if skipped
```

## Invalid Combination Handling

Invalid combinations should be skipped, not silently converted into something else.

The preview should show skipped combinations with clear reasons.

Examples:

```text
TrueCrypt + SHA-256:
  skipped because SHA-256 is a VeraCrypt PRF, not a TrueCrypt hash choice

TrueCrypt + Streebog-512:
  skipped because Streebog-512 is VeraCrypt-only

TrueCrypt + BLAKE2s-256:
  skipped because BLAKE2s-256 is VeraCrypt-only

TrueCrypt + Argon2id:
  skipped because Argon2id is VeraCrypt-only

TrueCrypt + Camellia:
  skipped because Camellia is VeraCrypt-only

TrueCrypt + Kuznyechik:
  skipped because Kuznyechik is VeraCrypt-only

VeraCrypt + TrueCrypt-only mode:
  skipped because selected family is VeraCrypt

Normal volume header + boot mode:
  skipped because non-system headers should not use system / boot modes

System header + non-system mode:
  skipped because system headers should use system / boot modes

VeraCrypt + BLAKE2s-256:
  valid VeraCrypt PRF, but skipped unless installed Hashcat reports a compatible supported mode

VeraCrypt + Argon2id:
  valid VeraCrypt KDF, but skipped unless installed Hashcat reports a compatible supported mode

VeraCrypt + GOST89:
  legacy VeraCrypt compatibility only; skipped unless compatibility table and installed Hashcat both support it
```

The app should not hide these skipped options completely. Greyed-out options with reasons are better than invisible rules.

## Manual Hashcat Mode Override

Manual override should be available as an advanced option.

Rules:

```text
Manual override must still use a normalized workspace header or a workspace-derived hash input.
Manual override must never use the original full volume as Hashcat input.
Manual override must not bypass workspace path safety rules.
Manual override must be saved in the job draft metadata.
Manual override should be checked against the installed Hashcat mode list when possible.
Manual override should warn if it conflicts with selected family, header type, or installed Hashcat support.
```

Suggested warning:

```text
Manual mode override bypasses the app’s normal VeraCrypt / TrueCrypt mode mapping. Use it only if you know this Hashcat mode is correct for the selected header. The job will still use workspace-local input and workspace-local output paths.
```

## Preview Before Job Generation

The app should require a mode preview before job drafts are finalized.

The preview should include:

```text
Target name
Target ID
Header ID
Normalized header path
Source / volume type
Header candidate type
Selected family
Selected encryption assumptions
Selected hash / PRF / KDF assumptions
Try-everything-valid status
OR entries
Expanded combinations
Skipped combinations
Duplicate modes removed
Final Hashcat modes
Current vs legacy mode status
Installed Hashcat support status
Required input format
Possible opener/version notes
Warnings
```

Suggested preview summary:

```text
Selected entries: 3
Expanded combinations: 42
Skipped invalid combinations: 18
Skipped unsupported-by-Hashcat combinations: 6
Duplicate modes removed: 9
Final runnable Hashcat modes: 9
```

Step 6 should not calculate final job count across PIMs, keyfiles, password sources, or queue behavior.

That belongs to later steps.

## Possible Opener / Version Notes

The app may show opener/version notes as hints, not guarantees.

Suggested field:

```text
possible_opener_version_notes
```

Important wording:

```text
These notes are compatibility hints based on the selected assumptions. The app cannot confirm which program version can open the volume until the correct combination is recovered and the volume is tested by the user.
```

Suggested notes:

```text
TrueCrypt family:
  Likely openable by TrueCrypt 7.1a.
  VeraCrypt 1.25.9 may be used for TrueCrypt mounting or conversion.
  VeraCrypt 1.26 and later removed TrueCrypt mode support.

VeraCrypt RIPEMD160 legacy:
  Legacy VeraCrypt compatibility.
  VeraCrypt 1.26 and later removed RIPEMD160 support for legacy volumes.
  VeraCrypt 1.25.9 may be needed to mount or convert.

VeraCrypt GOST89 legacy:
  Legacy VeraCrypt compatibility.
  VeraCrypt 1.26 and later removed GOST89 support.
  VeraCrypt 1.25.9 may be needed to mount or convert.

VeraCrypt BLAKE2s-256:
  Requires a VeraCrypt version that supports BLAKE2s-256.
  Check installed VeraCrypt documentation/version before assuming mount support.

VeraCrypt Argon2id:
  Requires a VeraCrypt version that supports Argon2id.
  No separate hash algorithm is selected for Argon2id.

VeraCrypt Camellia / Kuznyechik:
  VeraCrypt-only encryption algorithms.
  Not valid for TrueCrypt volumes.
```

The app should not claim that Hashcat success proves which GUI version can open the volume. It should only provide practical notes.

## Saved Mode Set Schema

Suggested saved mode set fields:

```text
schema_version
mode_set_id
target_id
header_id
normalized_header_path
source_category
volume_possibility
candidate_type
created_timestamp
updated_timestamp
try_everything_valid_enabled
manual_override_enabled
entries
expanded_modes
skipped_combinations
deduplicated_modes
final_runnable_modes
warnings
possible_opener_version_notes
```

Suggested entry fields:

```text
entry_id
container_family_selection
source_volume_type_selection
candidate_type_selection
encryption_selection
hash_prf_kdf_selection
include_current_modes
include_legacy_modes
include_unsupported_for_preview
manual_mode_override
notes
```

Suggested expanded mode fields:

```text
expanded_mode_id
entry_id
container_family
source_volume_type
candidate_type
encryption_algorithm
cipher_group
hash_prf_kdf
hashcat_mode
hashcat_mode_name
mode_generation
required_input_format
valid_for_container_family
supported_by_installed_hashcat
skip_reason
duplicate_of
possible_opener_version_notes
```

## App Behavior

The app should:

```text
load selected target and header metadata
work only from normalized 512-byte workspace headers
pre-fill source and header type from Step 5 metadata
allow family selection as VeraCrypt, TrueCrypt, or Both / Unknown
include a Try Every Valid VeraCrypt / TrueCrypt Mode option
show all relevant source / volume type cases
allow all valid family-specific encryption choices
allow all valid family-specific hash / PRF / KDF choices
prevent TrueCrypt selections from using VeraCrypt-only options
prevent VeraCrypt selections from using TrueCrypt-only options
support OR-style mode entries
expand unknown selections into valid combinations
map encryption algorithms into XTS groups
map family, header type, PRF/KDF, and XTS group to Hashcat mode numbers
prefer current Hashcat modes when available
support legacy Hashcat modes when current modes are unavailable or the user chooses them
parse installed Hashcat mode support after Hashcat setup
skip invalid combinations
show skipped combinations and reasons
deduplicate duplicate mode results
show required Hashcat input format for each mode
show possible opener/version notes as hints
allow manual Hashcat mode override with warnings
save mode sets inside the workspace
update job drafts with selected hash mode sets
save immediately after creating or changing a mode set
```

## Files Created or Modified

This step may create or modify:

```text
jobs/drafts/job_<job_id>.json
jobs/command-previews/hash_modes_preview_<job_id>.txt
generated/recipes/hash_mode_set_<mode_set_id>.json
generated/commands/hash_input_requirement_<job_id>.json
headers/metadata/header_<header_id>.json
targets/targets.json
logs/app/*
logs/errors/*
cleanup/cleanup-manifest.json
workspace.json
settings.json
```

If a later implementation adds derived `$truecrypt$` or `$veracrypt$` input files, those derived files must be created inside the workspace and recorded in the cleanup manifest.

## Workspace Folders Used

This step uses:

```text
jobs/drafts/
jobs/command-previews/
generated/recipes/
generated/commands/
headers/metadata/
targets/
logs/app/
logs/errors/
cleanup/
```

This step should not use:

```text
system temp folders
external folders by default
original volume files as Hashcat input
```

## Safety Rules

The hash mode builder must follow these rules:

```text
only support legitimate recovery of user-owned or authorized volumes
do not crack passwords itself
do not run Hashcat
do not modify original VeraCrypt or TrueCrypt volumes
do not use original target files as Hashcat input
only use normalized workspace headers as the source for mode building
keep mode sets and previews inside the workspace
treat mode selections as forensic-trail data
do not use system temp folders
do not upload, transmit, or exfiltrate headers, metadata, commands, mode sets, or previews
do not claim secure deletion is guaranteed
describe cleanup as trace centralization and minimization
manual override must not bypass workspace safety rules
manual override must not bypass normalized-header-only rules
invalid combinations must be skipped and shown to the user
unsupported-by-installed-Hashcat combinations must be shown clearly before skipping
```

## Open Questions

Open questions for later steps:

```text
exact UI layout for compatibility validation
exact command used to parse installed Hashcat mode support
whether current Hashcat modes require workspace-derived $truecrypt$ / $veracrypt$ text input files in all cases
where to store derived Hashcat input files if needed
whether to block manual override modes not reported by installed Hashcat or allow with warning
how final job-count preview combines hash modes with PIMs, keyfiles, and password sources
whether future Hashcat versions add VeraCrypt BLAKE2s-256 support
whether future Hashcat versions add VeraCrypt Argon2id support
whether future Hashcat versions add more VeraCrypt Camellia or Kuznyechik-specific mappings
whether backup header candidates are added later
```

## Final Decisions

```text
The hash mode builder maps selected assumptions to Hashcat -m mode numbers.
The builder works from normalized 512-byte headers inside the workspace.
The builder must never use original volume files as Hashcat input.
The builder must explicitly represent all source / volume type cases from Step 5.
The builder must support normal file containers and hidden-volume file-container candidates.
The builder must support normal non-system partition/device headers and hidden non-system partition/device headers.
The builder must support normal non-system disk/image headers and hidden non-system disk/image headers.
The builder must support normal system partition/device headers and hidden-system / hidden-OS candidates.
The builder must support normal system disk/image headers and hidden-system / hidden-OS image candidates.
Normal and hidden non-system headers use the same Hashcat mode families.
The difference between normal and hidden non-system volumes is the extracted header candidate, not the Hashcat -m mode.
System and hidden-system candidates use system / boot mode families.
Hidden system candidates must not be presented as normal hidden volumes.
The app supports VeraCrypt, TrueCrypt, and Both / Unknown.
The app must include a Try Every Valid VeraCrypt / TrueCrypt Mode option for users who know only that the header is from a VeraCrypt or TrueCrypt volume.
Try Every Valid mode expands only hash mode assumptions, not passwords, PIMs, keyfiles, or queue behavior.
The app must include all family-valid encryption choices.
TrueCrypt choices must be limited to TrueCrypt-supported encryption and hash/PRF choices.
VeraCrypt choices may include VeraCrypt-supported current and legacy encryption and PRF/KDF choices.
The app must prevent or clearly reject TrueCrypt + VeraCrypt-only combinations.
The app must prevent or clearly reject VeraCrypt + TrueCrypt-only combinations.
The app should keep a built-in mode compatibility table.
The app should also parse installed Hashcat support and use that result to decide what can actually be generated as runnable jobs.
The app should distinguish valid-for-container from supported-by-installed-Hashcat.
The app should prefer current Hashcat modes when available.
The app may use legacy modes when the installed Hashcat supports them and current modes are not available or the user chooses legacy behavior.
The app should support OR-style mode entries.
The app should expand unknown selections into valid combinations.
The app should map encryption algorithms to XTS 512-bit, 1024-bit, or 1536-bit groups.
The app should deduplicate duplicate mode results.
Duplicate jobs should not be created just because multiple selected encryption names map to the same Hashcat mode.
Invalid combinations should be skipped.
Skipped combinations should be shown in the preview with reasons.
Unsupported-by-installed-Hashcat combinations should be shown in the preview with reasons.
Manual Hashcat -m override should be allowed as an advanced option.
Manual override must still use workspace-local input.
Manual override must not bypass workspace safety rules.
Manual override must not allow original volumes as Hashcat input.
The app should show possible opener/version notes as hints, not guarantees.
The app should warn that VeraCrypt 1.26 and later removed TrueCrypt mode support, RIPEMD160 legacy mounting support, and GOST89 legacy mounting support.
The app should note that VeraCrypt BLAKE2s-256 and Argon2id require VeraCrypt versions that support those KDF/PRF choices.
The app should not claim it can determine the actual opening program version from header bytes alone.
Step 6 should save hash mode sets inside the workspace.
Step 6 should update job drafts but should not generate final full queue jobs by itself.
Step 6 should not handle PIM expansion, keyfile expansion, password generation, queue running, or reporting.
```

## Reference Notes

These references were used to inform the compatibility and mode-mapping assumptions for this step:

```text
Hashcat example hashes:
https://hashcat.net/wiki/doku.php?id=example_hashes

VeraCrypt release notes:
https://veracrypt.io/en/Release%20Notes.html

VeraCrypt encryption algorithms:
https://veracrypt.io/en/Encryption%20Algorithms.html

VeraCrypt hash algorithms:
https://veracrypt.io/en/Hash%20Algorithms.html

VeraCrypt Argon2id:
https://veracrypt.io/en/Argon2id.html

VeraCrypt conversion guide for 1.26 and later:
https://veracrypt.io/en/Conversion_Guide_VeraCrypt_1.26_and_Later.html

TrueCrypt encryption algorithms:
https://www.truecrypt.org/docs/encryption-algorithms

TrueCrypt cascades:
https://www.truecrypt.org/docs/cascades

TrueCrypt hash algorithms:
https://www.truecrypt.org/docs/hash-algorithms
```
