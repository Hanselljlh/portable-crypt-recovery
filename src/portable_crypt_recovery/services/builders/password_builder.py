"""Password candidate builder."""

from __future__ import annotations

import warnings
from itertools import product
from pathlib import Path

from portable_crypt_recovery.core.ids import new_id
from portable_crypt_recovery.core.paths import to_workspace_relative
from portable_crypt_recovery.models.password_source import PasswordSource

# Candidate count limits
_WARN_ABOVE = 100_000
_REQUIRE_CONFIRM_ABOVE = 1_000_000
_BLOCK_ABOVE = 10_000_000


class PasswordLimitWarning(UserWarning):
    pass


class PasswordLimitConfirmRequired(Exception):
    pass


class PasswordLimitBlocked(Exception):
    pass


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)
    return output


def combine_segments(segments: list[list[str]]) -> list[str]:
    """Combine ordered segment variants and preserve first-seen order."""
    if not segments:
        return []
    return dedupe_preserve_order(["".join(parts) for parts in product(*segments)])


def count_candidates(segments: list[list[str]]) -> int:
    """Count unique candidates without generating them (fast upper bound)."""
    if not segments:
        return 0
    total = 1
    for seg in segments:
        total *= len(seg)
    return total


def build_manual_password_source(
    passwords: list[str],
    workspace_root: Path,
    force: bool = False,
) -> PasswordSource:
    """Write a manual password list wordlist to the workspace.

    Parameters
    ----------
    passwords:
        List of plaintext passwords.
    workspace_root:
        Workspace root.
    force:
        Bypass limit checks.
    """
    _check_limits(len(passwords), force)
    source_id = new_id("pwsrc")
    out_path = workspace_root / "generated" / "wordlists" / f"{source_id}.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(passwords) + "\n", encoding="utf-8")
    rel = to_workspace_relative(out_path, workspace_root)
    return PasswordSource(
        source_id=source_id,
        source_type="manual",
        workspace_relative_path=rel,
        candidate_count=len(passwords),
    )


def build_wordlist_source(
    wordlist_path: Path,
    workspace_root: Path,
    is_external: bool = False,
) -> PasswordSource:
    """Reference an existing wordlist file as a password source.

    If inside the workspace, records a relative path.
    If external, records is_external=True.
    """
    if not wordlist_path.exists():
        raise FileNotFoundError(f"Wordlist not found: {wordlist_path}")
    source_id = new_id("pwsrc")
    try:
        rel = to_workspace_relative(wordlist_path, workspace_root)
        is_external = False
    except ValueError:
        rel = str(wordlist_path)
        is_external = True

    # Count lines for candidate_count (best-effort)
    count = 0
    try:
        with wordlist_path.open("r", encoding="utf-8", errors="replace") as fh:
            for _ in fh:
                count += 1
    except OSError:
        count = 0

    return PasswordSource(
        source_id=source_id,
        source_type="wordlist",
        workspace_relative_path=rel,
        is_external=is_external,
        candidate_count=count,
    )


def build_generated_password_source(
    segments: list[list[str]],
    workspace_root: Path,
    force: bool = False,
) -> PasswordSource:
    """Generate passwords from segment combinations and write to workspace.

    Parameters
    ----------
    segments:
        Each element is a list of variant strings for that position.
        The result is the Cartesian product, deduped, preserving order.
    workspace_root:
        Workspace root.
    force:
        Bypass limit checks.
    """
    upper_bound = count_candidates(segments)
    _check_limits(upper_bound, force)

    candidates = combine_segments(segments)
    _check_limits(len(candidates), force)

    source_id = new_id("pwsrc")
    out_path = workspace_root / "generated" / "wordlists" / f"{source_id}.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(candidates) + "\n", encoding="utf-8")
    rel = to_workspace_relative(out_path, workspace_root)

    return PasswordSource(
        source_id=source_id,
        source_type="generated",
        workspace_relative_path=rel,
        candidate_count=len(candidates),
    )


def _check_limits(count: int, force: bool) -> None:
    if force:
        return
    if count > _BLOCK_ABOVE:
        raise PasswordLimitBlocked(
            f"Candidate count {count} exceeds hard block limit {_BLOCK_ABOVE}."
        )
    if count > _REQUIRE_CONFIRM_ABOVE:
        raise PasswordLimitConfirmRequired(
            f"Candidate count {count} requires confirmation."
        )
    if count > _WARN_ABOVE:
        warnings.warn(
            f"Candidate count {count} exceeds {_WARN_ABOVE}.",
            PasswordLimitWarning,
            stacklevel=3,
        )
