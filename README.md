# Portable Crypt Recovery (PCR)

A local, portable Windows and Linux GUI for authorized VeraCrypt and TrueCrypt
volume recovery using Hashcat. All data stays on your machine — no cloud,
no telemetry.

> **Authorized use only.** You must own the volume or have explicit written
> authorization before attempting recovery. See [docs/safety-notes.txt](docs/safety-notes.txt).

## Quick start (portable release)

1. Download the latest release zip/tarball from the [Releases](../../releases) page.
2. Extract to any folder.
3. Place `hashcat.exe` (Windows) or `hashcat` (Linux) and its support files into
   `tools/hashcat/`.
4. Run `PCR.exe` (Windows) or `./PCR` (Linux).
5. **Settings → Hashcat Setup** — browse to `tools/hashcat/hashcat.exe` and click
   **Verify Hashcat**.
6. **Settings → Workspace** — open the pre-created `workspaces/default/` folder
   or create a new workspace.
7. **Targets** — add your VeraCrypt/TrueCrypt volume and extract its header.
8. **Jobs** — create a draft, select a wordlist, and expand to queue jobs.
9. **Queue** — click **Start Queue** and wait for results.
10. **Reports** — view cracked results and copy the recovered password.

## User guide

| Page | Description |
|------|-------------|
| [Getting Started](docs/user-guide/getting-started.md) | Installation, first run, workspace setup |
| [Hashcat Setup](docs/user-guide/hashcat-setup.md) | Configuring and verifying Hashcat |
| [Adding Targets](docs/user-guide/adding-targets.md) | Adding volumes and extracting headers |
| [Creating Jobs](docs/user-guide/creating-jobs.md) | Draft parameters, expansion, wordlists |
| [Running the Queue](docs/user-guide/running-queue.md) | Start, pause, resume, skip |
| [Reports](docs/user-guide/reports.md) | Viewing results, copying passwords, exporting |
| [Troubleshooting](docs/user-guide/troubleshooting.md) | Common issues and fixes |
| [Safety Notes](docs/safety-notes.txt) | Legal and security guidance |

## Core design rules

- Local desktop GUI only — no network calls, no telemetry.
- Hashcat is the required backend. PCR does not implement cracking itself.
- Original volumes are opened **read-only** and are never modified.
- Hashcat jobs use workspace-local 512-byte normalized header copies.
- All sensitive files stay inside the workspace folder you configure.
- System temp folders are never used for recovery data.
- Commands are stored and executed as argument arrays, never raw shell strings.

## Version 1 scope

- VeraCrypt and TrueCrypt file containers, disk images, and pre-extracted headers
- Hashcat setup and verification
- Hash mode, PIM, keyfile, and dictionary password builders
- One-job-at-a-time queue runner with pause/resume/skip
- Cracked-result report packages with clipboard auto-clear

Version 1 does not support raw physical disk or partition access.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .\.venv\Scripts\Activate.ps1    # Windows PowerShell
python -m pip install -e .[dev]
python -m pytest
python -m portable_crypt_recovery
```

## Building a portable release

**Windows:**
```powershell
.\packaging\windows\build.ps1 -Version "0.1.33"
# Output: dist\PCR-windows-portable-0.1.33.zip
```

**Linux:**
```bash
bash packaging/linux/build.sh 0.1.33
# Output: dist/PCR-linux-portable-0.1.33.tar.gz
```

## Hashcat

Hashcat is not bundled. Download it from <https://hashcat.net/hashcat/> and
verify the official checksums before use.

## License

MIT License. See [LICENSE](LICENSE).
