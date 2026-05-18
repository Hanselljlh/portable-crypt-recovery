"""Hashcat device scan."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class DeviceScanResult:
    ok: bool
    stdout: str
    stderr: str
    devices: list[dict] = field(default_factory=list)
    error: str | None = None


def scan_devices(executable_path: Path, timeout_seconds: int = 30) -> DeviceScanResult:
    """Run hashcat --backend-info and return parsed device list."""
    args = [str(executable_path.resolve()), "--backend-info"]
    try:
        completed = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return DeviceScanResult(ok=False, stdout="", stderr="", error=str(exc))

    combined = completed.stdout + completed.stderr
    return DeviceScanResult(
        ok=completed.returncode == 0,
        stdout=completed.stdout,
        stderr=completed.stderr,
        devices=parse_backend_info(combined),
        error=None if completed.returncode == 0 else "Hashcat backend info failed.",
    )


# ---------------------------------------------------------------------------
# Parser for hashcat 7.x --backend-info output
#
# Format example:
#   Backend Device ID #01 (Alias: #02)
#     Name...........: NVIDIA GeForce RTX 4070 Laptop GPU
#     ...
#
#   Backend Device ID #02 (Alias: #01)
#     Name...........: NVIDIA GeForce RTX 4070 Laptop GPU
#     ...
#
# Each "Backend Device ID #N" block is one device entry.
# The Alias field identifies which CUDA ↔ OpenCL ID maps to the same physical
# device; we include it so the UI can show "CUDA #1 = OpenCL #2 (RTX 4070)".
# ---------------------------------------------------------------------------

_DEVICE_HEADER = re.compile(r"Backend Device ID #(\d+)", re.IGNORECASE)
_NAME_LINE = re.compile(r"Name\.*:\s*(.+)", re.IGNORECASE)
_TYPE_LINE = re.compile(r"Type\.*:\s*(.+)", re.IGNORECASE)
_VENDOR_LINE = re.compile(r"Vendor\.*:\s*(.+)", re.IGNORECASE)
_ALIAS_LINE = re.compile(r"Alias:\s*#(\d+)", re.IGNORECASE)


def parse_backend_info(output: str) -> list[dict]:
    """Parse hashcat 7.x --backend-info output into a list of device dicts.

    Each dict has:
      id     (int)  — backend device ID as used by hashcat's -d flag
      label  (str)  — short display label, e.g. "Device #1"
      name   (str)  — device name, e.g. "NVIDIA GeForce RTX 4070 Laptop GPU"
      type   (str)  — "GPU" | "CPU" | "" (from Type field if present)
      vendor (str)  — vendor string if present
      alias  (int | None) — ID of the paired device in the other backend
    """
    devices: list[dict] = []
    current: dict | None = None

    for line in output.splitlines():
        stripped = line.strip()

        m_header = _DEVICE_HEADER.search(stripped)
        if m_header:
            # Save previous block
            if current is not None:
                devices.append(current)
            dev_id = int(m_header.group(1))
            # Pick up alias from the same line if present: "(Alias: #02)"
            m_alias = _ALIAS_LINE.search(stripped)
            alias = int(m_alias.group(1)) if m_alias else None
            current = {
                "id": dev_id,
                "label": f"Device #{dev_id}",
                "name": "",
                "type": "",
                "vendor": "",
                "alias": alias,
            }
            continue

        if current is None:
            continue

        if not current["name"]:
            m = _NAME_LINE.match(stripped)
            if m:
                current["name"] = m.group(1).strip()
                current["label"] = f"Device #{current['id']}  {current['name']}"
                continue

        if not current["type"]:
            m = _TYPE_LINE.match(stripped)
            if m:
                current["type"] = m.group(1).strip()
                continue

        if not current["vendor"]:
            m = _VENDOR_LINE.match(stripped)
            if m:
                current["vendor"] = m.group(1).strip()
                continue

    if current is not None:
        devices.append(current)

    # De-duplicate: CUDA and OpenCL expose the same physical GPU under different
    # backend device IDs (linked by Alias).  Keep all entries so the user can
    # choose CUDA (#1) or OpenCL (#2) explicitly, but mark duplicates.
    seen_names: dict[str, int] = {}
    for dev in devices:
        name = dev["name"]
        if name in seen_names:
            dev["duplicate_of"] = seen_names[name]
        else:
            seen_names[name] = dev["id"]

    return devices
