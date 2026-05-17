"""Application entry point."""

from __future__ import annotations

import sys

from portable_crypt_recovery.app.application import run_app


def main(argv: list[str] | None = None) -> int:
    """Run the GUI application."""
    return run_app(sys.argv if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
