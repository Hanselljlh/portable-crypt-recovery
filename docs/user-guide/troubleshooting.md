# Troubleshooting

## Hashcat is not found / not verified

**Symptom:** "Hashcat: Not configured" on the Dashboard. Start Queue is greyed out.

**Fix:**
1. Go to **Settings → Hashcat Setup**.
2. Click **Browse** and navigate to `hashcat.exe` (Windows) or `hashcat` (Linux).
3. Click **Verify Hashcat**. The version string should appear.
4. Click **Save**.

If Hashcat lives in `tools/hashcat/` inside the portable folder, PCR may detect
it automatically on startup. Make sure the filename is exactly `hashcat.exe` (Windows)
or `hashcat` (Linux) with no version suffix.

---

## "No pending jobs in queue" when I click Start Queue

All jobs may already have a non-`pending` status. In the **Queue** view:
- Select any exhausted or failed jobs and click **Restart Selected** to reset them to `pending`.
- Check that you have expanded at least one draft (Jobs → select draft → **Expand Draft**).

---

## Jobs fail immediately with "no wordlist_path"

The draft was created before the wordlist field was added, or the wordlist
path was not set. Re-create the draft:
1. Go to **Jobs**, click **New Draft**.
2. Under **Password Source**, select **Wordlist file** and browse to your `.txt` file.
3. Click **Save & Expand**.

---

## "Wordlist not found" error on queue start

The wordlist file was moved, renamed, or deleted after the draft was created.
1. Locate your wordlist file.
2. In **Jobs**, delete the affected drafts and create new ones pointing to the
   correct path.

---

## Queue starts then immediately stops

Check the queue status label. Common causes:
- All jobs were already in a terminal state (cracked, exhausted, failed, skipped).
- Hashcat exited with an error. Open the report folder for the failed job and
  check `stats.txt` and `command-used.txt` for the Hashcat error message.

---

## "Stale queue lock detected" on startup

The app was closed while the queue was running. Click **Yes** to remove the
stale lock. If you are unsure whether another instance is still running against
the same workspace, click **No** and check for running Hashcat processes first.

---

## Password not copied / clipboard auto-clear too fast

Go to **Settings → Preferences** and increase the **Clipboard auto-clear timeout**
(default: 60 seconds). Set to 0 to disable auto-clear entirely.

---

## Extracted header is all zeros / wrong size

This can happen if:
- The file is not a VeraCrypt or TrueCrypt container.
- The container uses a non-standard header offset (e.g. a custom bootloader).
- The file is a sparse file whose zero-filled blocks were not read correctly.

Try opening the file in the original TrueCrypt/VeraCrypt application to confirm
it is a valid container before attempting recovery.

---

## The GUI is blank / crashes on startup (Linux)

PySide6 requires certain system libraries. Install them with:

```bash
sudo apt-get install libgl1-mesa-glx libegl1 libxkbcommon-x11-0 libdbus-1-3
```

On RPM-based systems:
```bash
sudo dnf install mesa-libGL libxkbcommon-x11 dbus-libs
```

---

## Collecting logs for a bug report

See [Diagnostic Bundle](diagnostic-bundle.md) for instructions on collecting
logs and workspace metadata to include in a bug report.

Application log: `logs/pcr.log` in the portable root folder.
