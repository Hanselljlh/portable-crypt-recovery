# Hashcat Setup

## Obtaining Hashcat

Download Hashcat from: https://hashcat.net/hashcat/

PCR supports Hashcat 6.x and later.

## Portable Installation (Recommended)

Place the Hashcat binary in:

```
PCR/tools/hashcat/hashcat.exe   (Windows)
PCR/tools/hashcat/hashcat        (Linux)
```

PCR will automatically find it in the portable tools folder.

## System PATH Installation

If Hashcat is on your system PATH, PCR will find it automatically.

## Manual Path

You can also browse to any location in **Settings → Hashcat Setup → Browse**.

## Verification

After setting the path, click **Verify** to confirm:
- The executable exists and is runnable
- The version string is readable
- Hashcat returns exit code 0 for `--version`

## Device Selection

Click **Scan Devices** to detect available compute devices (GPUs, CPUs).
Select the devices to use for cracking in the device list.

## Supported Modes

PCR uses these Hashcat mode families:

| Family     | Modes (current) | Modes (legacy) |
|------------|-----------------|----------------|
| TrueCrypt  | 29311-29343     | 6211-6243      |
| VeraCrypt  | 29411-29483     | 13711-13783    |

Current modes are preferred when supported by the installed Hashcat build.
