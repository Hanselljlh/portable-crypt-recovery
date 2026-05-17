# Adding Targets

A **target** is the encrypted volume you want to recover access to.
PCR supports VeraCrypt and TrueCrypt file containers, disk image files, and
pre-extracted header files.

## Supported target types

| Type | Description |
|------|-------------|
| File container | A VeraCrypt or TrueCrypt `.vc`, `.tc`, or custom-extension container file |
| Disk image | A raw image of a full disk or partition (`.img`, `.dd`, `.raw`) |
| Pre-extracted header | A 512-byte header file you already extracted from another tool |

> **Note:** PCR never modifies the original volume file. It opens it read-only
> to extract a normalized 512-byte header copy for Hashcat.

## Adding a target

1. Open a workspace (see [Getting Started](getting-started.md)).
2. Navigate to **Targets** in the left sidebar.
3. Click **Add Target**.
4. In the dialog:
   - **Label** — a short name to identify this target (e.g. "My backup drive")
   - **Volume type** — select VeraCrypt or TrueCrypt
   - **Container type** — File Container, Disk Image, or Pre-extracted Header
   - **Source file** — browse to the volume or header file
5. Click **Save Target**.

## Extracting headers

After saving a target, go to the **Headers** tab and click **Extract Headers**
to scan the target for normal, hidden, and system headers. PCR tries three offsets:

| Header type | Offset |
|-------------|--------|
| Normal | Byte 0 |
| Hidden | Byte 65536 |
| System (encrypted OS) | Byte 31744 |

Extracted headers are stored as 512-byte `.bin` files in `headers/normalized/`
inside your workspace.

## What happens to the original file?

Nothing. PCR reads the first 128 KiB of your volume to look for header
candidates, then closes the file. The original is never written to.

## Removing a target

Select the target in the list and click **Remove**. This removes the target
record from `targets/targets.json`. It does not delete any extracted headers
or jobs that were already created from this target.
