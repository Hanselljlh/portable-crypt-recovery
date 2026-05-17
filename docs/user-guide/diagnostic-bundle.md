# Diagnostic Bundle

If you need to report a bug or seek support, you can collect a diagnostic bundle
to share with developers. The bundle contains log files and non-sensitive
workspace metadata — it never includes passwords, header binaries, or volume files.

## What is collected

- Application log files from `logs/`
- `workspace.json` (workspace ID, name, created timestamp)
- `settings.json` with sensitive fields redacted (passwords removed)
- Queue state summary (job IDs, statuses, modes — no passwords)
- Platform and Python version information

## What is NOT collected

- Recovered passwords or any cracked results
- Normalized header `.bin` files
- Keyfile copies
- Original volume files
- Hashcat potfile contents

## Creating a bundle (manual method)

Until a one-click export is added to the GUI:

1. Locate your workspace folder (shown in the Dashboard or Settings → Workspace).
2. Copy the `logs/` folder.
3. Copy `workspace.json` and `settings.json` (remove `hashcat_path` if it reveals
   sensitive filesystem paths you prefer not to share).
4. Open an issue at: https://github.com/Hanselljlh/portable-crypt-recovery/issues
5. Attach the files and describe what you were doing when the problem occurred.

## Log file location

Application logs are written to `logs/pcr.log` inside the portable folder root
(not inside the workspace). If no workspace is open, this is the only log file.

Workspace-specific logs (if any) are in `<workspace>/logs/`.

## Privacy

PCR does not transmit any data automatically. All diagnostics are collected
manually and shared only when you choose to share them.
