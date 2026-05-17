"""Tests for the password builder."""

import pytest

from portable_crypt_recovery.services.builders.password_builder import (
    PasswordLimitBlocked,
    PasswordLimitConfirmRequired,
    PasswordLimitWarning,
    build_generated_password_source,
    build_manual_password_source,
    build_wordlist_source,
    combine_segments,
    count_candidates,
    dedupe_preserve_order,
)


def test_combine_segments_preserves_order_and_dedupes():
    assert combine_segments([["dog", "Dog"], ["1", "1"]]) == ["dog1", "Dog1"]


def test_combine_segments_empty():
    assert combine_segments([]) == []


def test_combine_segments_single_segment():
    assert combine_segments([["a", "b", "c"]]) == ["a", "b", "c"]


def test_count_candidates():
    assert count_candidates([["a", "b"], ["1", "2", "3"]]) == 6
    assert count_candidates([]) == 0
    assert count_candidates([["x"]]) == 1


def test_dedupe_preserve_order():
    assert dedupe_preserve_order(["a", "b", "a", "c"]) == ["a", "b", "c"]


def test_build_manual_password_source_creates_file(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    src = build_manual_password_source(["pass1", "pass2", "hunter2"], ws)
    assert src.source_type == "manual"
    assert src.candidate_count == 3
    assert src.workspace_relative_path is not None
    wl_file = ws / src.workspace_relative_path
    assert wl_file.exists()
    content = wl_file.read_text(encoding="utf-8")
    assert "pass1" in content
    assert "hunter2" in content


def test_build_manual_password_source_empty_list(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    src = build_manual_password_source([], ws)
    assert src.candidate_count == 0


def test_build_generated_password_source(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    segments = [["dog", "cat"], ["123", "456"]]
    src = build_generated_password_source(segments, ws)
    assert src.source_type == "generated"
    assert src.candidate_count == 4  # dog123, dog456, cat123, cat456
    wl_file = ws / src.workspace_relative_path
    assert wl_file.exists()


def test_build_wordlist_source_internal(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    wl = ws / "inputs" / "wordlists" / "imported" / "list.txt"
    wl.parent.mkdir(parents=True)
    wl.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    src = build_wordlist_source(wl, ws)
    assert src.source_type == "wordlist"
    assert src.candidate_count == 3
    assert not src.is_external


def test_build_wordlist_source_external(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    # Wordlist outside workspace
    external_wl = tmp_path / "external_list.txt"
    external_wl.write_text("a\nb\n", encoding="utf-8")
    src = build_wordlist_source(external_wl, ws)
    assert src.is_external
    assert src.candidate_count == 2


def test_password_limit_warn(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    # 100_001 unique passwords
    passwords = [str(i) for i in range(100_001)]
    with pytest.warns(PasswordLimitWarning):
        src = build_manual_password_source(passwords, ws)
    assert src.candidate_count == 100_001


def test_password_limit_confirm_required(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    passwords = [str(i) for i in range(1_000_001)]
    with pytest.raises(PasswordLimitConfirmRequired):
        build_manual_password_source(passwords, ws)


def test_password_limit_force_bypass(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    passwords = [str(i) for i in range(1_000_001)]
    src = build_manual_password_source(passwords, ws, force=True)
    assert src.candidate_count == 1_000_001
