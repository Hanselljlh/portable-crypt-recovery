"""Tests for keyfile normalization and combination builder."""

import pytest

from portable_crypt_recovery.models.keyfile_set import KeyfileEntry
from portable_crypt_recovery.services.builders.keyfile_builder import (
    KEYFILE_USED_BYTES_LIMIT,
    KeyfileLimitBlocked,
    KeyfileLimitConfirmRequired,
    KeyfileLimitWarning,
    _count_combinations,
    build_keyfile_combinations,
    import_keyfile,
    normalize_keyfile,
)


def test_normalize_small_keyfile(tmp_path):
    source = tmp_path / "key.bin"
    dest = tmp_path / "out" / "key.bin"
    source.write_bytes(b"abc")
    capped = normalize_keyfile(source, dest)
    assert capped is False
    assert dest.read_bytes() == b"abc"


def test_normalize_large_keyfile_caps_to_first_mib(tmp_path):
    source = tmp_path / "large.bin"
    dest = tmp_path / "out" / "large.bin"
    source.write_bytes(b"a" * (KEYFILE_USED_BYTES_LIMIT + 10))
    capped = normalize_keyfile(source, dest)
    assert capped is True
    assert len(dest.read_bytes()) == KEYFILE_USED_BYTES_LIMIT


def test_normalize_exactly_mib(tmp_path):
    source = tmp_path / "exact.bin"
    dest = tmp_path / "out" / "exact.bin"
    source.write_bytes(b"z" * KEYFILE_USED_BYTES_LIMIT)
    capped = normalize_keyfile(source, dest)
    assert capped is False
    assert len(dest.read_bytes()) == KEYFILE_USED_BYTES_LIMIT


def test_import_keyfile_creates_workspace_entry(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    source = tmp_path / "mykey.bin"
    source.write_bytes(b"hello keyfile")

    entry = import_keyfile(source, ws)
    assert entry.keyfile_id.startswith("keyfile_")
    assert entry.size_bytes == len(b"hello keyfile")
    assert entry.sha256 != ""
    assert "inputs/keyfiles/normalized" in entry.normalized_workspace_path
    # File should exist on disk
    dest = ws / entry.normalized_workspace_path
    assert dest.exists()
    assert dest.read_bytes() == b"hello keyfile"


def test_import_keyfile_missing_source(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    with pytest.raises(FileNotFoundError):
        import_keyfile(tmp_path / "nonexistent.bin", ws)


def test_build_keyfile_combinations_single(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    src = tmp_path / "k1.bin"
    src.write_bytes(b"key1")
    e1 = import_keyfile(src, ws)

    combos = build_keyfile_combinations([e1])
    assert len(combos) == 1
    assert combos[0].entries == [e1]


def test_build_keyfile_combinations_two_keys(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    src1 = tmp_path / "k1.bin"
    src1.write_bytes(b"key1")
    src2 = tmp_path / "k2.bin"
    src2.write_bytes(b"key2")
    e1 = import_keyfile(src1, ws)
    e2 = import_keyfile(src2, ws)

    # max_per_set=1 => 2 single-key combos
    combos = build_keyfile_combinations([e1, e2], max_per_set=1)
    assert len(combos) == 2

    # max_per_set=2 => 2 single + 1 pair = 3
    combos2 = build_keyfile_combinations([e1, e2], max_per_set=2)
    assert len(combos2) == 3


def _make_dummy_entries(n: int) -> list[KeyfileEntry]:
    return [
        KeyfileEntry(
            keyfile_id=f"keyfile_{i:04d}",
            original_path=f"/fake/{i}.bin",
            normalized_workspace_path=f"inputs/keyfiles/normalized/keyfile_{i:04d}.bin",
            size_bytes=10,
            sha256="abc",
        )
        for i in range(n)
    ]


def test_keyfile_combinations_warn_above_100():
    entries = _make_dummy_entries(8)
    # 2^8 - 1 = 255 combos with max_per_set=8 (all subsets)
    with pytest.warns(KeyfileLimitWarning):
        combos = build_keyfile_combinations(entries, max_per_set=8)
    assert len(combos) == 255


def test_keyfile_combinations_force_bypasses_limit():
    entries = _make_dummy_entries(8)
    combos = build_keyfile_combinations(entries, max_per_set=8, force=True)
    assert len(combos) == 255


# ---------------------------------------------------------------------------
# _count_combinations — pre-expansion count helper
# ---------------------------------------------------------------------------


def test_count_combinations_single_per_set():
    # n entries, max 1 per set => n combos
    assert _count_combinations(5, 1) == 5


def test_count_combinations_all_subsets():
    # 2^n - 1 non-empty subsets
    assert _count_combinations(4, 4) == 15
    assert _count_combinations(8, 8) == 255


def test_count_combinations_capped_max_per_set():
    # max_per_set > n => same as max_per_set = n
    assert _count_combinations(3, 99) == _count_combinations(3, 3)


# ---------------------------------------------------------------------------
# Limit enforcement happens before list construction
# ---------------------------------------------------------------------------


def test_limits_checked_before_expansion_block():
    """KeyfileLimitBlocked must raise before any KeyfileSet is built."""
    # 17 entries, max_per_set=17 => 2^17-1 = 131071 > 100_000
    entries = _make_dummy_entries(17)
    with pytest.raises(KeyfileLimitBlocked):
        build_keyfile_combinations(entries, max_per_set=17)


def test_limits_checked_before_expansion_confirm():
    """KeyfileLimitConfirmRequired must raise before any KeyfileSet is built."""
    # 14 entries, max_per_set=14 => 2^14-1 = 16383, between 10_000 and 100_000
    entries = _make_dummy_entries(14)
    with pytest.raises(KeyfileLimitConfirmRequired):
        build_keyfile_combinations(entries, max_per_set=14)


def test_limits_checked_before_expansion_warn():
    """KeyfileLimitWarning must fire before itertools builds the list."""
    entries = _make_dummy_entries(8)
    # Confirm the warning is raised (pre-expansion path)
    with pytest.warns(KeyfileLimitWarning):
        build_keyfile_combinations(entries, max_per_set=8)


def test_force_bypasses_block():
    entries = _make_dummy_entries(17)
    # Should not raise even though count > _BLOCK_ABOVE
    combos = build_keyfile_combinations(entries, max_per_set=17, force=True)
    assert len(combos) == (2**17 - 1)


# ---------------------------------------------------------------------------
# Acceptance tests: combinations vs permutations, source not modified
# ---------------------------------------------------------------------------


def test_build_keyfile_combinations_not_permutations(tmp_path):
    """3 keyfiles → 7 sets (C(3,1)+C(3,2)+C(3,3)), not 15 (permutations)."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    entries = []
    for i in range(3):
        src = tmp_path / f"k{i}.bin"
        src.write_bytes(f"key{i}".encode())
        entries.append(import_keyfile(src, ws))

    combos = build_keyfile_combinations(entries, max_per_set=3)
    assert len(combos) == 7  # 3 + 3 + 1


def test_build_keyfile_combinations_no_duplicates(tmp_path):
    """Each combination set must have a unique set_id."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    entries = []
    for i in range(3):
        src = tmp_path / f"k{i}.bin"
        src.write_bytes(f"key{i}".encode())
        entries.append(import_keyfile(src, ws))

    combos = build_keyfile_combinations(entries, max_per_set=3)
    set_ids = [c.set_id for c in combos]
    assert len(set_ids) == len(set(set_ids))


def test_import_keyfile_does_not_modify_source(tmp_path):
    """The original keyfile must be untouched after import."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    source = tmp_path / "key.bin"
    original_bytes = b"sensitive keyfile data"
    source.write_bytes(original_bytes)

    import_keyfile(source, ws)

    assert source.read_bytes() == original_bytes
