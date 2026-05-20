"""Password candidate builder."""

from __future__ import annotations

import itertools
import warnings
from pathlib import Path

from portable_crypt_recovery.core.ids import new_id
from portable_crypt_recovery.core.paths import to_workspace_relative
from portable_crypt_recovery.models.password_source import PasswordSource

# Candidate count limits
_WARN_ABOVE = 100_000
_REQUIRE_CONFIRM_ABOVE = 1_000_000
_BLOCK_ABOVE = 10_000_000

# Common leet-speak substitutions (lowercase key → substituted character).
# Only ONE substitution per character to keep combo count manageable.
_LEET: dict[str, str] = {
    "a": "@", "e": "3", "i": "1", "o": "0",
    "s": "$", "t": "7", "l": "1", "g": "9",
}


class PasswordLimitWarning(UserWarning):
    pass


class PasswordLimitConfirmRequired(Exception):
    pass


class PasswordLimitBlocked(Exception):
    pass


# All 52 ASCII letters used by the ?C pattern token.
_LETTERS_A_Z: list[str] = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")


def expand_pattern_tokens(text: str) -> list[str]:
    """Expand ``?C`` tokens in *text* to all 52 letter variants.

    Each ``?C`` in the string is independently replaced by every letter
    a–z and A–Z.  Multiple ``?C`` tokens multiply the result size:
    ``"?C?C"`` yields 52 × 52 = 2 704 strings.

    If no ``?C`` token is present the original string is returned as-is
    inside a one-element list.
    """
    if "?C" not in text:
        return [text]
    parts = text.split("?C")
    num_tokens = len(parts) - 1
    results: list[str] = []
    for combo in itertools.product(_LETTERS_A_Z, repeat=num_tokens):
        s = parts[0]
        for i, letter in enumerate(combo):
            s += letter + parts[i + 1]
        results.append(s)
    return dedupe_preserve_order(results)


def case_variants(word: str) -> list[str]:
    """Generate all case combinations for the alphabetic characters in *word*.

    Non-alphabetic characters are preserved in place.  The result is
    deduped so that words with no alphabetic characters return a single
    element.

    Example::

        case_variants("a1b") == ["a1b", "a1B", "A1b", "A1B"]
    """
    alpha_idx = [i for i, c in enumerate(word) if c.isalpha()]
    if not alpha_idx:
        return [word]
    chars = list(word)
    results: list[str] = []
    for combo in itertools.product(*[[chars[i].lower(), chars[i].upper()] for i in alpha_idx]):
        variant = chars[:]
        for idx, c in zip(alpha_idx, combo, strict=True):
            variant[idx] = c
        results.append("".join(variant))
    return dedupe_preserve_order(results)


def permutation_variants(word: str) -> list[str]:
    """Generate all unique character permutations of *word*.

    Duplicate permutations (arising from repeated characters) are removed
    while preserving first-seen order.

    Example::

        permutation_variants("ab") == ["ab", "ba"]
        permutation_variants("aa") == ["aa"]
    """
    return dedupe_preserve_order(["".join(p) for p in itertools.permutations(word)])


def estimate_qc_expansion_count(text: str) -> int:
    """Return the count that ``expand_pattern_tokens(text)`` would produce, without expanding.

    Uses ``52 ** num_tokens``; returns 1 when no ``?C`` token is present.
    Safe to call on arbitrarily long patterns — no allocation is performed.
    """
    n = text.count("?C")
    return 1 if n == 0 else 52 ** n


def estimate_permutation_count(word: str) -> int:
    """Return ``factorial(len(word))`` — an upper bound for ``permutation_variants(word)``.

    The true unique-permutation count may be smaller when characters repeat, but
    this upper bound is sufficient as a pre-expansion safety guard.
    Safe to call on any length — no allocation is performed.
    """
    import math
    return math.factorial(len(word))


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
    return dedupe_preserve_order(["".join(parts) for parts in itertools.product(*segments)])


def count_candidates(segments: list[list[str]]) -> int:
    """Count unique candidates without generating them (fast upper bound)."""
    if not segments:
        return 0
    total = 1
    for seg in segments:
        total *= len(seg)
    return total


def leet_variants(word: str) -> list[str]:
    """Generate all leet-speak combinations for *word*.

    Each character that has a known leet substitution (see ``_LEET``) is
    either kept as-is or replaced by its leet equivalent.  The result is the
    Cartesian product of all keep/replace decisions, deduped.

    Example::

        leet_variants("sale") → ["sale", "s@le", "sal3", "s@l3", ...]
    """
    leet_positions: list[tuple[int, str, str]] = [
        (i, c, _LEET[c.lower()])
        for i, c in enumerate(word)
        if c.lower() in _LEET
    ]
    if not leet_positions:
        return [word]
    chars = list(word)
    results: list[str] = []
    for combo in itertools.product(*[[False, True] for _ in leet_positions]):
        variant = chars[:]
        for use_leet, (i, orig, sub) in zip(combo, leet_positions, strict=True):
            variant[i] = sub if use_leet else orig
        results.append("".join(variant))
    return dedupe_preserve_order(results)


def number_suffix_variants(
    word: str,
    start: int,
    stop: int,
    zero_pad: int = 0,
    prefix: bool = False,
) -> list[str]:
    """Append (or prepend) every integer from *start* to *stop* inclusive.

    Parameters
    ----------
    zero_pad:
        If > 0, left-pad numbers to this width with zeros.  E.g. ``zero_pad=2``
        produces ``"01"`` for 1.
    prefix:
        If True, prepend the number instead of appending it.
    """
    results: list[str] = []
    for n in range(start, stop + 1):
        suffix = str(n).zfill(zero_pad) if zero_pad > 0 else str(n)
        results.append(suffix + word if prefix else word + suffix)
    return dedupe_preserve_order(results)


def year_suffix_variants(
    word: str,
    start: int = 1990,
    stop: int = 2025,
    prefix: bool = False,
) -> list[str]:
    """Append (or prepend) every year from *start* to *stop* inclusive."""
    results: list[str] = []
    for y in range(start, stop + 1):
        year_str = str(y)
        results.append(year_str + word if prefix else word + year_str)
    return dedupe_preserve_order(results)


def special_char_variants(
    word: str,
    chars: list[str],
    position: str = "append",
) -> list[str]:
    """Append and/or prepend each string in *chars* to *word*.

    Parameters
    ----------
    chars:
        Sequences to attach (e.g. ``["!", "@", "!@#"]``).
    position:
        ``"append"`` | ``"prepend"`` | ``"both"``
    """
    results: list[str] = []
    for ch in chars:
        if position in ("append", "both"):
            results.append(word + ch)
        if position in ("prepend", "both"):
            results.append(ch + word)
    return dedupe_preserve_order(results)


def reverse_variant(word: str) -> list[str]:
    """Return the word and its reverse (deduped if palindrome)."""
    return dedupe_preserve_order([word, word[::-1]])


# ---------------------------------------------------------------------------
# Wordlist nickname / metadata helpers
# ---------------------------------------------------------------------------

def save_wordlist_meta(txt_path: Path, nickname: str, candidate_count: int) -> None:
    """Write a JSON sidecar file ``<name>.meta.json`` alongside *txt_path*."""
    import json
    from datetime import UTC, datetime

    meta = {
        "nickname": nickname.strip(),
        "candidate_count": candidate_count,
        "created_at": datetime.now(UTC).isoformat(),
    }
    meta_path = txt_path.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def load_wordlist_meta(txt_path: Path) -> dict:
    """Return the parsed sidecar dict, or ``{}`` if not present / unreadable."""
    import json

    meta_path = txt_path.with_suffix(".meta.json")
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_wordlist_nickname(txt_path: Path) -> str:
    """Return the stored nickname for *txt_path*, or ``""`` if none."""
    return load_wordlist_meta(txt_path).get("nickname", "")


def rename_wordlist_nickname(txt_path: Path, new_name: str) -> None:
    """Update (or create) the sidecar with a new nickname."""
    import json

    meta = load_wordlist_meta(txt_path)
    meta["nickname"] = new_name.strip()
    if "candidate_count" not in meta:
        try:
            with txt_path.open(encoding="utf-8", errors="replace") as _fh:
                meta["candidate_count"] = sum(1 for _ in _fh)
        except OSError:
            meta["candidate_count"] = 0
    meta_path = txt_path.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


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
    nickname: str = "",
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
    nickname:
        Human-readable name saved in a ``.meta.json`` sidecar alongside the
        wordlist.  Shown in the job picker instead of the raw filename.
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

    if nickname.strip():
        save_wordlist_meta(out_path, nickname.strip(), len(candidates))

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
