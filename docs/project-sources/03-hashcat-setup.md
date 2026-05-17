# 03-hashcat-setup.md

## Purpose

This step defines how the app finds, stores, verifies, and remembers Hashcat.

Hashcat is the required backend for the Portable VeraCrypt/TrueCrypt Recovery GUI project.

The app does not crack passwords itself. The app prepares and manages Hashcat jobs through a controlled backend layer.

This step does not design job running, queue resume, header extraction, hash mode selection, PIM handling, keyfile handling, password building, or reports. Those are handled in later steps.

The goals for Hashcat setup are:

- make Hashcat easy to locate
- support Windows and Linux
- support portable use by default
- support a user-selected tools folder
- verify Hashcat with `--version`
- detect available compute devices after Hashcat is verified
- avoid unsafe raw shell command building
- keep John the Ripper optional later, not required now
- keep version 1 simple by not auto-downloading Hashcat

## User Inputs

The Hashcat setup screen should accept:

- existing Hashcat executable path
- selected Hashcat tools folder
- choice to use the portable app tools folder
- choice to use a custom tools folder
- choice to open the official Hashcat download page
- selected compute devices after detection
- choice to re-check Hashcat version
- choice to re-scan available devices
- choice to repair a missing or moved Hashcat path

Expected executable names:

```text
Windows:
hashcat.exe

Linux:
hashcat
hashcat.bin
```

The app should not require the user to manually type paths if browsing is possible.

## Hashcat Setup Screen

The Settings screen should include a Hashcat Setup section.

Suggested layout:

```text
Hashcat Status
- Not configured
- Found but not verified
- Verified
- Missing
- Error

Hashcat Path
- Current path
- Browse
- Use Portable Tools Folder
- Use Custom Tools Folder
- Re-check

Download / Install Help
- Open Official Hashcat Download Page
- User Downloads Hashcat Manually

Version
- Detected version
- Last checked timestamp
- Check Again

Devices
- Scan Devices
- Detected devices
- Selected devices
```

The Dashboard should show a warning when Hashcat is not configured or fails verification.

Suggested Dashboard warning:

```text
Hashcat is not configured. Open Settings → Hashcat Setup to locate Hashcat or open the official download page.
```

## Hashcat Location Options

The app should support these Hashcat location methods.

### 1. Portable Tools Folder

Default portable location:

```text
PCR/tools/hashcat/
```

Expected executable examples:

```text
Windows:
PCR/tools/hashcat/hashcat.exe

Linux:
PCR/tools/hashcat/hashcat
PCR/tools/hashcat/hashcat.bin
```

This should be the preferred location for portable use.

Hashcat binaries and Hashcat support files may live outside the workspace because they are tools, not recovery project data.

Sensitive recovery data must not be stored in the tools folder.

### 2. User-Selected Tools Folder

The user may choose a custom tools folder.

Example:

```text
D:/RecoveryTools/hashcat/
~/tools/hashcat/
```

If the custom tools folder is outside the portable app folder, the app should mark it as external and less portable.

This is allowed because Hashcat itself is not sensitive project data.

The app should warn:

```text
This Hashcat tools folder is outside the portable app folder. The workspace can still be portable, but this Hashcat path may need to be repaired if the project is moved to another computer.
```

### 3. Browse for Existing Hashcat

The user may browse directly to an existing Hashcat executable.

The app should validate the selected file before saving it.

Validation checks:

- file exists
- file is not a folder
- filename looks like `hashcat.exe`, `hashcat`, or `hashcat.bin`
- file can be executed
- `hashcat --version` runs successfully
- version output is captured

The app should not accept an executable path as verified until `--version` succeeds.

### 4. System PATH Detection

The app may optionally detect Hashcat from the system PATH.

This should not be the preferred portable mode.

If detected from PATH, the app should show:

```text
Hashcat was found from the system PATH. This may not be portable. For portable use, place Hashcat inside the portable tools folder.
```

The user may accept the detected path or choose a portable copy instead.

### 5. Official Download Page

Version 1 will not auto-download Hashcat.

The user is responsible for downloading their preferred Hashcat version.

If Hashcat is missing, the app should offer:

```text
Browse for Existing Hashcat
Open Official Hashcat Download Page
Use Portable Tools Folder
```

The official download page should be opened in the user’s browser.

Suggested official page:

```text
https://hashcat.net/hashcat/
```

The app should not direct users to third-party download sites.

### 6. No Auto-Download in Version 1

Version 1 should not download Hashcat automatically.

Auto-download is out of scope for the first version because it adds avoidable complexity, including:

- changing download URLs
- repository or release location changes
- archive format differences
- checksum or signature verification
- extraction behavior
- executable permissions
- antivirus or browser warnings on Windows
- dependency or runtime confusion
- update handling

Opening the official Hashcat download page is enough for version 1.

Auto-download may be reconsidered later, but it should not be part of the first build.

## Hashcat Verification

The app should verify Hashcat by running:

```text
hashcat --version
```

Internally, this must be built as an argument array.

Example internal form:

```text
["path/to/hashcat", "--version"]
```

The GUI may show a command preview, but the backend must not build unsafe raw shell strings.

The app should capture:

- executable path
- detected version text
- exit code
- stdout
- stderr
- check timestamp
- operating system
- whether verification passed or failed

Suggested success status:

```text
Hashcat verified.
Version: <detected version>
Path: <path>
```

Suggested failure status:

```text
Hashcat could not be verified. Check that the selected file is the real Hashcat executable and that required drivers or permissions are available.
```

The app should save verification status after a successful check.

The app should re-check Hashcat:

- when the path changes
- when the user presses Check Again
- when opening a workspace with a missing Hashcat path
- before starting the first queue run
- after app updates if needed

## Windows Path Handling

Windows support should handle:

- `hashcat.exe`
- drive letters
- removable drive path changes
- spaces in folder names
- long paths where possible
- relative paths inside the portable app folder

The app must pass paths as process arguments, not as manually quoted shell text.

Good internal argument handling:

```text
["D:/PCR/tools/hashcat/hashcat.exe", "--version"]
```

Avoid unsafe shell handling:

```text
"D:/PCR/tools/hashcat/hashcat.exe --version"
```

If the portable folder moves and the Hashcat path was inside it, the app should repair the path using a relative stored path.

If the selected Hashcat path is missing, the app should show repair options:

```text
Locate Hashcat
Use Portable Tools Folder
Open Official Download Page
Ignore for Now
```

## Linux Path Handling

Linux support should handle:

- `hashcat`
- `hashcat.bin`
- executable permission checks
- mounted drive path changes
- case-sensitive paths
- relative paths inside the portable app folder

The app should check whether the selected file has execute permission.

If execute permission is missing, the app should show:

```text
Hashcat exists but is not executable. Mark it executable or choose a different Hashcat file.
```

The app may offer a helper action later, but it should not silently change permissions without user approval.

Linux command execution must also use argument arrays.

Example internal form:

```text
["/home/user/PCR/tools/hashcat/hashcat.bin", "--version"]
```

## Path Storage Rules

Hashcat path storage should follow the portability rules from Step 2.

If Hashcat is inside the portable app folder, store it as a portable-relative path when possible.

Example:

```text
tools/hashcat/hashcat.exe
tools/hashcat/hashcat.bin
```

If Hashcat is outside the portable app folder, store it as an absolute external tool path.

External tool paths should be marked as non-portable.

Hashcat path data may be stored in:

```text
PCR/config/app-global-settings.json
workspace/settings.json
```

Suggested behavior:

- app-global settings store the default Hashcat path for the app
- workspace settings may override the Hashcat path for a specific workspace
- workspace settings should store selected compute devices for that workspace
- sensitive recovery data must not be stored in app-global settings

Hashcat path settings are not passwords, but they may still reveal tool usage. Keep stored data minimal.

## Device Detection

After Hashcat is verified, the app should allow device detection.

The app should detect available devices using Hashcat itself.

Suggested check:

```text
hashcat --backend-info
```

or the equivalent supported Hashcat backend information option.

Internally, use an argument array.

Example:

```text
["path/to/hashcat", "--backend-info"]
```

The app should parse device information enough to show user-friendly choices.

Device categories should include:

```text
NVIDIA GPU
AMD GPU
Intel GPU
CPU
Other accelerator, if reported by Hashcat
```

The app should support:

- one GPU
- multiple GPUs
- CPU only
- GPU plus CPU
- mixed vendors
- no usable devices detected

The app should not require CPU use by default if GPUs are available.

The app should allow the user to select one, several, or all detected devices.

Suggested UI labels:

```text
Use fastest detected GPU only
Use selected GPUs
Use CPU only
Use GPU plus CPU
Custom device selection
```

Device selection should be saved in workspace settings because different workspaces may use different performance preferences.

Exact Hashcat command arguments for selected devices are handled later when job commands are built.

## Driver and Runtime Handling

The app should not try to install GPU drivers, CUDA, HIP, OpenCL, or other runtimes in the first version.

If Hashcat reports missing drivers or missing runtimes, the app should show the error clearly and suggest installing the correct vendor driver/runtime.

Suggested warning:

```text
Hashcat is installed, but no usable compute device was detected. Install or update your GPU or CPU compute runtime, then scan devices again.
```

The app should not hide Hashcat errors.

The app should store setup errors in workspace logs or app startup logs depending on context.

## Backend Tools Decision

Hashcat is required.

John the Ripper is not required for the first version.

The app should not block setup because John the Ripper is missing.

The Settings screen may later include an Optional Tools section, but Step 3 only requires Hashcat.

Decision:

```text
Required backend:
Hashcat

Optional later backend:
John the Ripper
```

The first version should avoid designing around John the Ripper unless a later step explicitly adds it.

## App Behavior

The app should:

- show Hashcat setup status on the Dashboard and Settings screen
- look for Hashcat in the portable tools folder first
- allow the user to browse for Hashcat
- allow a custom tools folder
- optionally detect Hashcat from PATH
- open the official Hashcat download page when Hashcat is missing
- not auto-download Hashcat in version 1
- let the user download and choose their preferred Hashcat version
- verify Hashcat using `--version`
- save verified Hashcat path and version metadata
- detect devices after verification
- let the user choose available compute devices
- save selected compute devices in workspace settings
- handle Windows and Linux paths safely
- use argument arrays for Hashcat checks
- avoid unsafe shell strings
- show clear repair options if Hashcat is moved or missing
- not require John the Ripper now

## Files Created or Modified

This step may create or modify these portable app files:

```text
PCR/config/app-global-settings.json
PCR/tools/hashcat/*
PCR/logs/app-startup.log
```

This step may create or modify these workspace files:

```text
workspace/settings.json
logs/app/*
logs/errors/*
cleanup/cleanup-manifest.json
```

Hashcat itself should usually be stored in:

```text
PCR/tools/hashcat/
```

or in a user-selected tools folder.

Hashcat verification logs may be stored in app logs or workspace logs depending on when setup happens.

Hashcat setup files must not contain:

- passwords
- password candidates
- keyfile contents
- extracted headers
- normalized job headers
- cracked results
- generated commands for recovery jobs
- potfile data
- restore data

## Workspace Folders Used

This step mainly uses:

```text
logs/app/
logs/errors/
cleanup/
```

Later Hashcat jobs will use:

```text
hashcat/sessions/
hashcat/restore/
hashcat/potfile/
hashcat/logs/
hashcat/output/
jobs/command-arrays/
jobs/command-previews/
```

This step only prepares Hashcat setup. It does not run recovery jobs yet.

## Safety Rules

The app must follow these rules:

- only support legitimate recovery of user-owned volumes
- Hashcat is used only as a local backend
- do not upload targets, headers, passwords, candidates, keyfiles, logs, or results
- do not silently transmit anything
- do not process original volumes directly with Hashcat
- do not use Hashcat until an extracted or normalized header job exists
- verify Hashcat with `--version` before use
- build Hashcat checks as argument arrays
- do not build unsafe shell strings
- keep sensitive recovery files inside the workspace
- keep Hashcat potfile, restore files, logs, outputs, and job command data inside the workspace during job execution
- do not use the system temp folder for recovery project data
- do not claim secure deletion is guaranteed
- describe cleanup as trace centralization and minimization
- do not require John the Ripper in the first version
- do not auto-download Hashcat in version 1

## Open Questions

Open questions for later steps:

- exact Hashcat command arguments for running queued jobs
- exact command arguments for selected devices
- exact behavior for pause now
- exact behavior for pause after current job
- exact Hashcat restore behavior
- exact potfile path argument
- exact output path argument
- exact status JSON parsing
- exact benchmark or speed test behavior
- whether auto-download is reconsidered after version 1
- whether PGP signature verification is added if auto-download is ever added later

## Final Decisions

- Hashcat is the required backend.
- John the Ripper is optional later and not required now.
- The app should prefer Hashcat inside the portable app tools folder.
- Default Hashcat folder is `PCR/tools/hashcat/`.
- The user may choose a custom tools folder.
- The user may browse for an existing Hashcat executable.
- The app may optionally detect Hashcat from PATH, but PATH detection is not the preferred portable mode.
- Version 1 will not auto-download Hashcat.
- The user is responsible for downloading their preferred Hashcat version.
- The app will provide an option to open the official Hashcat download page.
- The app will let the user browse to an existing Hashcat executable.
- The app will support placing Hashcat in the portable `tools/hashcat/` folder.
- Auto-download may be reconsidered later, but it is out of scope for version 1 because download URLs, archive formats, verification, extraction, permissions, and repository changes add avoidable complexity.
- If Hashcat is missing, the app should offer to browse, use the portable tools folder, or open the official Hashcat download page.
- The app should not direct users to third-party Hashcat download sites.
- Hashcat must be verified with `hashcat --version`.
- The app should not mark Hashcat as verified until the version check succeeds.
- Hashcat checks must be built as argument arrays.
- The GUI must not directly build unsafe shell command strings.
- Windows should look for `hashcat.exe`.
- Linux should look for `hashcat` or `hashcat.bin`.
- Linux should check executable permissions.
- Paths inside the portable app folder should be stored as relative paths where possible.
- External Hashcat paths should be marked as non-portable.
- The app should provide repair options when Hashcat is moved or missing.
- After Hashcat is verified, the app should scan available devices.
- Device detection should use Hashcat backend/device information.
- The app should show NVIDIA GPU, AMD GPU, Intel GPU, CPU, and other reported accelerators when available.
- The user should be able to select one, several, or all detected devices.
- Device choices should be saved in workspace settings.
- The app should not install GPU drivers or runtimes in the first version.
- Hashcat setup must not store passwords, headers, keyfiles, potfiles, restore files, cracked results, or generated recovery commands outside the workspace.
- Hashcat binaries may be stored outside the workspace because they are tools, not recovery project data.
