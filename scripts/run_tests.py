#!/usr/bin/env python3
"""Run the test suite from the repository root.

Usage:
    python scripts/run_tests.py [pytest-args]

Examples:
    python scripts/run_tests.py
    python scripts/run_tests.py -x -v
    python scripts/run_tests.py tests/unit/test_pim_builder.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent

args = [sys.executable, "-m", "pytest"] + sys.argv[1:]
if len(sys.argv) == 1:
    args += ["tests/", "-x", "-q"]

result = subprocess.run(args, cwd=str(repo_root))
raise SystemExit(result.returncode)
