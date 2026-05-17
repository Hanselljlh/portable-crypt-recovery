"""Hashcat device scan foundation."""

from __future__ import annotations

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
    """Run hashcat --backend-info as an argument array and keep raw output."""
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

    return DeviceScanResult(
        ok=completed.returncode == 0,
        stdout=completed.stdout,
        stderr=completed.stderr,
        devices=parse_backend_info(completed.stdout),
        error=None if completed.returncode == 0 else "Hashcat backend info failed.",
    )


def parse_backend_info(output: str) -> list[dict]:
    """Very small parser for early fake Hashcat tests."""
    devices: list[dict] = []
    for line in output.splitlines():
        clean = line.strip()
        if clean.lower().startswith("device") and ":" in clean:
            left, right = clean.split(":", 1)
            devices.append({"label": left.strip(), "name": right.strip()})
    return devices
