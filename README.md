# Portable VeraCrypt/TrueCrypt Recovery GUI

A local, portable Windows and Linux GUI for authorized VeraCrypt and TrueCrypt volume recovery using Hashcat.

## Project status

This repository is in the initial scaffold stage. The first implementation focuses on the app shell, workspace foundation, JSON-backed state, Hashcat setup plumbing, and testable backend services.

The app is not a general Hashcat GUI. It is a focused recovery workflow for user-owned or authorized VeraCrypt and TrueCrypt volumes.

## Core rules

- Local desktop GUI only.
- Hashcat is the required backend.
- The app does not crack passwords itself.
- Original VeraCrypt and TrueCrypt volumes are opened read-only and are never modified.
- Hashcat jobs must use workspace-local extracted or normalized headers, not original full volumes.
- App-created sensitive files and forensic-trail files stay inside the selected workspace by default.
- System temp folders must not be used for recovery project data.
- Commands are stored and executed internally as argument arrays, not unsafe raw shell strings.
- Command strings are only for preview or export.

## Version 1 scope

Version 1 targets:

- VeraCrypt and TrueCrypt file containers
- disk or drive image files
- already extracted header files
- workspace-local normalized 512-byte job headers
- Hashcat setup and verification
- mode, PIM, keyfile, and password builders
- one-job-at-a-time queue runner
- cracked-result reports

Version 1 does not support raw physical disk, drive, or partition access. Those options are future placeholders.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .[dev]
python -m pytest
python -m portable_crypt_recovery
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
python -m pytest
python -m portable_crypt_recovery
```

## Hashcat

Hashcat is not bundled by default. Place it in:

```text
PCR/tools/hashcat/
```

or browse to an existing Hashcat executable from Settings once the GUI is running.

Version 1 should not auto-download Hashcat.

## License

MIT License. See [LICENSE](LICENSE).
