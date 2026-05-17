# 00-final-build-decisions.md

## Purpose

This file captures final pre-build decisions for the Portable VeraCrypt/TrueCrypt Recovery GUI project.

Treat this file as higher priority than earlier source files where it clarifies naming, version 1 scope limits, future placeholders, and implementation limits.

Earlier source files remain valid unless directly clarified here.

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

Rationale:

The app should not be named as a general Hashcat GUI because it only supports a focused VeraCrypt and TrueCrypt recovery workflow. The word recovery should remain in the name to make the legitimate purpose clear.

## Version 1 Scope Limits

Version 1 supports:

- VeraCrypt and TrueCrypt file containers
- disk or drive image files
- already extracted header files
- workspace-local normalized 512-byte job headers
- Hashcat as the required backend

Version 1 does not support raw physical disk, raw physical drive, or raw physical partition access yet.

Raw physical disk, drive, and partition support should remain visible in the GUI only as disabled planned options marked:

```text
Future
```

This prevents the feature from being forgotten while keeping version 1 simpler and safer to build.

## Future Placeholders

The following features are planned for later and should have placeholders, reminders, or disabled GUI labels where appropriate:

- raw physical disk, drive, and partition access
- adjacent PIM range optimization
- recursive keyfile folder scanning
- optional Hashcat auto-download with checksum or signature verification
- optional John the Ripper backend

These should not block version 1.

## Password Candidate Limits

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

The app must not use system temp folders for password candidate data.

## Keyfile Combination Limits

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

Recursive keyfile scanning is future work.

The GUI may show recursive scanning as a disabled planned option marked:

```text
Future
```

## PIM Handling

Version 1 uses one exact PIM value per Hashcat job variant.

For a single exact PIM value, the command builder should set:

```text
--veracrypt-pim-start <value>
--veracrypt-pim-stop <value>
```

Default PIM behavior should be stored as:

```text
pim_mode: default
```

It should not be stored as a fake custom PIM value of `0`.

Adjacent PIM range optimization is future work.

A future implementation may combine adjacent PIM values into a single Hashcat range when doing so does not break reporting, queue tracking, or resume behavior.

## Keyfile Import Defaults

Optional full keyfile copies should default to off.

Optional thumbnail generation should default to off.

If enabled, full copies and thumbnails must stay inside the workspace and must be tracked in the cleanup manifest.

Hashcat jobs should use normalized workspace-local keyfile copies, not original keyfile paths by default.

## Manual Hashcat Mode Override

Manual Hashcat `-m` override should be allowed as an advanced option with a strong warning.

Manual override must still enforce these rules:

- use only workspace-local normalized headers or workspace-derived hash inputs
- never use original full volumes as Hashcat input
- keep potfile, restore files, logs, output files, and command data inside the workspace
- store command execution internally as an argument array
- never rely on unsafe raw shell strings for execution

If the selected manual mode is not reported by the installed Hashcat build, the app should warn the user but may allow the override if workspace safety rules are still satisfied.

## Derived Hash Input Files

If a Hashcat mode requires a derived `$truecrypt$` or `$veracrypt$` text input file instead of a raw 512-byte header file, the app should create that file inside:

```text
generated/hash-inputs/
```

Rules:

- derive only from the normalized workspace header
- do not read the original volume again
- do not use system temp folders
- track derived hash input files in the cleanup manifest
- treat derived hash input files as sensitive recovery strategy data

## Reports

Report regeneration should create versioned copies by default.

Overwriting existing reports should require user confirmation.

Reports should stay inside the workspace by default.

If the user exports reports outside the workspace, show the external-location cleanup warning and record the export in the cleanup manifest.

## Clipboard Handling

Copied recovered passwords should auto-clear from the clipboard after 60 seconds by default.

The user may disable clipboard auto-clear in settings.

The GUI should hide recovered passwords by default and require user action to reveal or copy them.

## Build Priority Rule

When building from the project source files, apply requirements in this order:

1. This file: `00-final-build-decisions.md`
2. Step source files `01` through `11`
3. Implementation-specific decisions made during coding

If a conflict appears, prefer this file for final naming and version 1 scope limits.
