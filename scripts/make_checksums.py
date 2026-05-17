#!/usr/bin/env python3
"""Generate SHA-256 checksums for release artifacts in dist/.

Usage:
    python scripts/make_checksums.py [dist_dir]

Writes checksums to dist/SHA256SUMS.txt and prints them.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ARTIFACT_GLOBS = ("*.zip", "*.tar.gz", "*.exe", "*.AppImage")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str]) -> int:
    dist_dir = Path(argv[1]) if len(argv) > 1 else Path("dist")
    if not dist_dir.is_dir():
        print(f"ERROR: dist dir not found: {dist_dir}", file=sys.stderr)
        return 1

    artifacts: list[Path] = []
    for pattern in ARTIFACT_GLOBS:
        artifacts.extend(dist_dir.glob(pattern))

    if not artifacts:
        print(f"No artifacts found in {dist_dir}", file=sys.stderr)
        return 1

    artifacts.sort()
    lines: list[str] = []
    for path in artifacts:
        digest = sha256_file(path)
        line = f"{digest}  {path.name}"
        lines.append(line)
        print(line)

    out = dist_dir / "SHA256SUMS.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nChecksums written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
