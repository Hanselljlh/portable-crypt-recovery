# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a Vulnerability

If you discover a security vulnerability in Portable VeraCrypt/TrueCrypt Recovery GUI, please do NOT open a public GitHub issue.

Instead, report it privately:

1. Open a **private** GitHub security advisory:
   - Go to the repository → Security → Advisories → New draft security advisory
2. Or contact the maintainers directly via GitHub.

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fix (optional)

We aim to respond within 7 days and to release a patch within 30 days for confirmed vulnerabilities.

## Security Design Principles

This application is designed with the following security principles:

- **No shell injection** — All Hashcat invocations use `subprocess` with argument list (never `shell=True`).
- **No system temp** — Recovery data never goes to system temp folders. Everything stays inside the workspace.
- **Workspace-relative paths** — Internal file references use relative paths to prevent path traversal.
- **Read-only source access** — Original volumes are opened with `open(..., 'rb')` only, never written to.
- **Passwords hidden by default** — Recovered passwords are masked in the UI by default.
- **Clipboard auto-clear** — Copied passwords are auto-cleared from the clipboard after 60 seconds.
- **No upload** — The app does not transmit headers, passwords, keyfiles, or any recovery data over the network.
- **Atomic writes** — All JSON state files use atomic writes (write to temp, then rename).
- **Cleanup manifest** — All workspace-generated files are tracked for user-controlled cleanup.
