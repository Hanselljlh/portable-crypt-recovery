# Getting Started

## What is Portable VeraCrypt/TrueCrypt Recovery GUI?

PCR is a portable desktop application for authorized recovery of VeraCrypt and TrueCrypt volume passwords using Hashcat as the cracking backend.

It is designed for:
- Recovering your own forgotten volume password
- Authorized forensic recovery of volumes you own or have written authorization to recover

## Requirements

- Windows 10/11 or Linux (Ubuntu 20.04+)
- Python 3.12+ (if running from source)
- PySide6 6.7+ (if running from source)
- Hashcat 6.x or later (not bundled — you must provide it)

## Setup

### Portable Folder Layout

```
PCR/
├── app/           — Application files
├── tools/
│   └── hashcat/   — Place hashcat.exe or hashcat here
├── workspaces/
│   └── default/   — Default workspace
├── config/        — App configuration
└── logs/          — Application logs
```

### Step 1: Launch the Application

Run `PCR.exe` (Windows) or `./PCR` (Linux), or from source:

```bash
python -m portable_crypt_recovery.main
```

### Step 2: Configure Hashcat

1. Go to **Settings**
2. Under **Hashcat Setup**, browse to your `hashcat.exe` or `hashcat` binary
3. Click **Verify** to confirm it works
4. Click **Scan Devices** to detect available compute devices

### Step 3: Add a Target Volume

1. Go to **Targets**
2. Click **Add Volume...**
3. Check the ownership confirmation checkbox
4. Select the source type (File Container, Disk/Drive Image, or Already Extracted Header)
5. Browse to the source file
6. Select which header candidates to extract
7. Click OK

### Step 4: Build Jobs

1. Go to **Jobs**
2. Configure hash mode, PIM, keyfile, and password source for your target
3. Click **Expand to Queue Jobs**

### Step 5: Run the Queue

1. Go to **Queue**
2. Review the job list
3. Click **Start Queue**

### Step 6: Review Results

When a password is found, a report is generated in:
```
<workspace>/reports/cracked/job_<id>_run_<id>/
```

The Reports view shows all cracked results. Passwords are hidden by default — click Reveal to show them.

## Important Notes

- PCR never transmits your data over the network
- Original volume files are opened read-only and never modified
- All recovery data stays inside your workspace
- Backup your workspace folder to preserve recovery progress
