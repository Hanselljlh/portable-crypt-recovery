"""Helpers for creating fake Hashcat fixtures in tests."""

from __future__ import annotations

from pathlib import Path


def write_fake_hashcat(path: Path) -> Path:
    """Create a small executable Python script that mimics basic Hashcat commands."""
    script = """#!/usr/bin/env python3
import sys
if '--version' in sys.argv:
    print('hashcat (fake) v0.0')
    raise SystemExit(0)
if '--backend-info' in sys.argv:
    print('Device #1: Fake CPU')
    raise SystemExit(0)
print('fake hashcat unsupported args', sys.argv[1:])
raise SystemExit(1)
"""
    path.write_text(script, encoding="utf-8")
    path.chmod(0o755)
    return path
