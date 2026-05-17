#!/usr/bin/env python3
"""Run the PCR GUI from the repository root.

Usage:
    python scripts/run_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src/ is on the path when running from repo root
repo_root = Path(__file__).parent.parent
src_dir = repo_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from portable_crypt_recovery.main import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
