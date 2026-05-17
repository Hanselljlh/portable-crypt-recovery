# Workspace Cleanup

## What Gets Created in Your Workspace

PCR stores all recovery data inside the workspace folder, including:

- Normalized 512-byte header copies (`headers/normalized/`)
- Imported header originals (`headers/imported/`)
- Normalized keyfile copies (`inputs/keyfiles/normalized/`)
- Generated wordlists (`generated/wordlists/`)
- Generated PIM lists (`generated/pim-lists/`)
- Hashcat potfiles, restore files, and output files (`hashcat/`)
- Reports and recovery packages (`reports/`)
- Logs (`logs/`)

## Cleanup Manifest

All workspace-generated files are tracked in:

```
cleanup/cleanup-manifest.json
```

This file records what was created, when, by which step, and its current status.

## What to Keep

After successful recovery, keep:
- The recovery package folder: `reports/cracked/job_<id>_run_<id>/`
- Specifically: `recovered-result.txt`, `recovered-result.json`, normalized header, keyfiles

## What to Delete After Recovery

When you no longer need the workspace data:

- Hashcat potfiles: `hashcat/potfile/` — contain cracked hashes
- Hashcat restore files: `hashcat/restore/` — session state
- Hashcat output files: `hashcat/output/` — raw outfile lines
- Generated wordlists: `generated/wordlists/`
- Generated PIM lists: `generated/pim-lists/`
- Normalized headers: `headers/normalized/` (after keeping recovery package)
- Normalized keyfiles: `inputs/keyfiles/normalized/`
- Logs: `logs/`

## Secure Deletion

PCR does not perform secure deletion. Deleting files via normal OS methods
leaves data recoverable with forensic tools. If you need secure deletion,
use a dedicated tool (e.g., `shred` on Linux, Eraser on Windows).

PCR describes cleanup as trace centralization and minimization — keeping
everything in one known location so you know what to clean up.
