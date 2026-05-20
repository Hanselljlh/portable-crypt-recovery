"""Keyfile normalization and combination builder."""

from __future__ import annotations

import contextlib
import hashlib
import itertools
import json
import math
import warnings
from pathlib import Path

from portable_crypt_recovery.core.ids import new_id
from portable_crypt_recovery.core.paths import to_workspace_relative
from portable_crypt_recovery.models.keyfile_set import KeyfileEntry, KeyfileSet

KEYFILE_USED_BYTES_LIMIT = 1_048_576  # 1 MiB

# Combination limits
_WARN_ABOVE = 100
_REQUIRE_CONFIRM_ABOVE = 10_000
_BLOCK_ABOVE = 100_000


class KeyfileLimitWarning(UserWarning):
    pass


class KeyfileLimitConfirmRequired(Exception):
    pass


class KeyfileLimitBlocked(Exception):
    pass


def normalize_keyfile(source: Path, destination: Path) -> bool:
    """Copy the bytes used by VeraCrypt/TrueCrypt keyfile handling.

    Returns True when the source was capped to the first 1 MiB.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as src:
        data = src.read(KEYFILE_USED_BYTES_LIMIT + 1)
    capped = len(data) > KEYFILE_USED_BYTES_LIMIT
    destination.write_bytes(data[:KEYFILE_USED_BYTES_LIMIT])
    return capped


def _sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def import_keyfile(
    source: Path,
    workspace_root: Path,
) -> KeyfileEntry:
    """Normalize a keyfile and save it to the workspace.

    Returns a KeyfileEntry with workspace-relative path.
    """
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"Keyfile not found: {source}")

    keyfile_id = new_id("keyfile")
    normalized_dir = workspace_root / "inputs" / "keyfiles" / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)
    dest = normalized_dir / f"keyfile_{keyfile_id}{source.suffix}"

    normalize_keyfile(source, dest)
    sha256 = _sha256_of(dest)
    size = dest.stat().st_size
    rel = to_workspace_relative(dest, workspace_root)

    return KeyfileEntry(
        keyfile_id=keyfile_id,
        original_path=str(source),
        normalized_workspace_path=rel,
        size_bytes=size,
        sha256=sha256,
    )


def _count_combinations(n: int, max_per_set: int) -> int:
    """Return the number of non-empty subsets of size ≤ max_per_set from n items."""
    return sum(math.comb(n, r) for r in range(1, min(max_per_set, n) + 1))


def build_keyfile_combinations(
    entries: list[KeyfileEntry],
    max_per_set: int = 1,
    force: bool = False,
) -> list[KeyfileSet]:
    """Generate all combinations of keyfile entries.

    Parameters
    ----------
    entries:
        Normalized keyfile entries to combine.
    max_per_set:
        Maximum number of keyfiles per combination set.
    force:
        Bypass confirmation/block limits.

    Returns a list of KeyfileSet objects, one per unique combination.
    """
    n = len(entries)
    count = _count_combinations(n, max_per_set)
    if not force:
        if count > _BLOCK_ABOVE:
            raise KeyfileLimitBlocked(
                f"Keyfile combination count {count} exceeds limit {_BLOCK_ABOVE}."
            )
        if count > _REQUIRE_CONFIRM_ABOVE:
            raise KeyfileLimitConfirmRequired(
                f"Keyfile combination count {count} requires confirmation."
            )
        if count > _WARN_ABOVE:
            warnings.warn(
                f"Keyfile combination count {count} exceeds {_WARN_ABOVE}.",
                KeyfileLimitWarning,
                stacklevel=2,
            )

    sets: list[KeyfileSet] = []
    for r in range(1, min(max_per_set, n) + 1):
        for combo in itertools.combinations(entries, r):
            sets.append(
                KeyfileSet(
                    set_id=new_id("kfset"),
                    entries=list(combo),
                )
            )
    return sets


# ---------------------------------------------------------------------------
# Named keyfile-set persistence  (user-created reusable keyfile configs)
# ---------------------------------------------------------------------------

def _named_kf_sets_dir(workspace_root: Path) -> Path:
    d = workspace_root / "generated" / "keyfile-sets"
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_named_keyfile_set(workspace_root: Path, ks: KeyfileSet) -> None:
    """Persist a user-created named keyfile set to the workspace."""
    from portable_crypt_recovery.core.atomic_write import atomic_write_json

    path = _named_kf_sets_dir(workspace_root) / f"{ks.set_id}.json"
    atomic_write_json(path, ks.to_dict())


def list_named_keyfile_sets(workspace_root: Path) -> list[KeyfileSet]:
    """Return all saved named keyfile sets, sorted by nickname."""
    result: list[KeyfileSet] = []
    for p in sorted(_named_kf_sets_dir(workspace_root).glob("*.json")):
        with contextlib.suppress(Exception):
            result.append(KeyfileSet.from_dict(json.loads(p.read_text(encoding="utf-8"))))
    return sorted(result, key=lambda s: s.nickname.lower())


def delete_named_keyfile_set(workspace_root: Path, set_id: str) -> bool:
    """Delete a named keyfile set by ID.  Returns True if deleted."""
    path = _named_kf_sets_dir(workspace_root) / f"{set_id}.json"
    if path.exists():
        path.unlink()
        return True
    return False


def load_named_keyfile_set(workspace_root: Path, set_id: str) -> KeyfileSet | None:
    """Load one named keyfile set by ID, or None if not found."""
    path = _named_kf_sets_dir(workspace_root) / f"{set_id}.json"
    if not path.exists():
        return None
    with contextlib.suppress(Exception):
        return KeyfileSet.from_dict(json.loads(path.read_text(encoding="utf-8")))
    return None
