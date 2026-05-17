# Reports

When Hashcat recovers a password, PCR automatically generates a **report
package** — a folder containing the recovered password, the header used, any
keyfiles, and supporting metadata.

## Viewing reports

1. Navigate to **Reports** in the sidebar.
2. Click **Refresh** to load the latest report list.
3. Select a report to see its details in the lower pane.

The list shows the timestamp, job ID prefix, and whether a password was recovered.

## Report package contents

Each report is stored in:
```
reports/cracked/job_<job_id>_run_<run_id>/
```

| File | Contents |
|------|---------|
| `recovered-result.txt` | Plain-text summary including the recovered password |
| `recovered-result.json` | Machine-readable version of the same data |
| `recovered-result.md` | Markdown summary (no password — use .txt/.json) |
| `normalized-header.bin` | The 512-byte header that was cracked |
| `keyfile_*.*` | Copies of any keyfiles used (if applicable) |
| `recovery-package-manifest.json` | Metadata (job ID, mode, PIM, etc.) |
| `stats.txt` | Raw Hashcat status output |
| `command-used.txt` | The Hashcat command that produced this result |
| `how-to-open.txt` | Instructions for mounting the volume |

> **Security:** `recovered-result.txt` and `recovered-result.json` contain
> the plaintext password. Keep this folder secure. Delete it when no longer needed.

## Copying the password

Select a report that shows **CRACKED** and click **Copy Password**. The password
is copied to your clipboard and will be automatically cleared after the configured
timeout (default 60 seconds).

## Opening the report folder

Click **Open Report Folder** to open the package directory in your file manager.

## Exporting a report

Click **Export Report Folder...** to copy the entire report package to a
location you choose (e.g. a USB drive or encrypted folder).

## How to open your volume

Once you have the recovered password:

1. Use [VeraCrypt](https://veracrypt.fr) or TrueCrypt 7.1a to mount the volume.
2. Select the volume file.
3. Enter the recovered password.
4. Select any keyfiles from the report package if required.

> **VeraCrypt 1.26+ note:** Support for legacy TrueCrypt volumes was removed.
> Use VeraCrypt 1.25.9 for TrueCrypt containers or volumes using RIPEMD-160/GOST89.
