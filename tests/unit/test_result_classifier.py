"""Tests for result_classifier — hashcat exit code mapping."""

import pytest
from pathlib import Path
from portable_crypt_recovery.services.queue.result_classifier import classify_result


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_exit_0_with_outfile_is_cracked(tmp_path):
    """Exit 0 = CRACKED; outfile contains hash:password."""
    out = tmp_path / "out.txt"
    _write(out, "$vc$abc:mysecret\n")
    r = classify_result(0, out, tmp_path / "pot.txt")
    assert r.status == "cracked"
    assert r.cracked_password == "mysecret"


def test_exit_0_empty_outfile_still_cracked(tmp_path):
    """Exit code 0 with no outfile content — still mark cracked (unusual but safe)."""
    out = tmp_path / "out.txt"
    out.write_text("", encoding="utf-8")
    r = classify_result(0, out, tmp_path / "pot.txt")
    assert r.status == "cracked"


def test_exit_1_is_exhausted(tmp_path):
    """Exit 1 = EXHAUSTED — all candidates tried, no match."""
    r = classify_result(1, tmp_path / "out.txt", tmp_path / "pot.txt")
    assert r.status == "exhausted"
    assert r.cracked_password is None


def test_exit_2_is_aborted(tmp_path):
    """Exit 2 = ABORTED — user stopped the run."""
    r = classify_result(2, tmp_path / "out.txt", tmp_path / "pot.txt")
    assert r.status == "aborted"


def test_exit_minus1_is_failed(tmp_path):
    """Exit -1 / 4294967295 = ERROR."""
    r = classify_result(4294967295, tmp_path / "out.txt", tmp_path / "pot.txt")
    assert r.status == "failed"


def test_outfile_takes_priority_over_exit_code(tmp_path):
    """Cracked password in outfile wins even when exit code signals error."""
    out = tmp_path / "out.txt"
    _write(out, "$vc$abc:found_it\n")
    r = classify_result(4294967295, out, tmp_path / "pot.txt")
    assert r.status == "cracked"
    assert r.cracked_password == "found_it"


def test_potfile_fallback(tmp_path):
    """Password in potfile is used when outfile is absent."""
    pot = tmp_path / "pot.txt"
    _write(pot, "$vc$abc:frompot\n")
    r = classify_result(1, tmp_path / "out.txt", pot)
    assert r.status == "cracked"
    assert r.cracked_password == "frompot"


def test_password_extraction_after_first_colon(tmp_path):
    """Passwords containing colons are preserved correctly."""
    out = tmp_path / "out.txt"
    _write(out, "hashdata:pass:word:with:colons\n")
    r = classify_result(0, out, tmp_path / "pot.txt")
    # split(":", 1) → ["hashdata", "pass:word:with:colons"]
    assert r.cracked_password == "pass:word:with:colons"
