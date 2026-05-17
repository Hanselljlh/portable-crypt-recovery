"""Tests for keyfile normalization and combination builder."""

import pytest

from portable_crypt_recovery.services.builders.keyfile_builder import (
    KEYFILE_USED_BYTES_LIMIT,
    KeyfileLimitBlocked,
    KeyfileLimitConfirmRequired,
    KeyfileLimitWarning,
    build_keyfile_combinations,
    import_keyfile,
    normalize_keyfile,
)
from portable_crypt_recovery.models.keyfile_set import KeyfileEntry


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
