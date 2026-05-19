"""Tests for the PIM output parser."""

from __future__ import annotations

from portable_crypt_recovery.services.hashcat.pim_output_parser import (
    extract_cracked_pim,
    extract_password_from_line,
)

# ---------------------------------------------------------------------------
# extract_cracked_pim
# ---------------------------------------------------------------------------

def test_extract_cracked_pim_dollar_format():
    """$PIM=485 format should return 485."""
    line = "$veracrypt$1$abc$def$PIM=485:mypassword"
    assert extract_cracked_pim(line) == 485


def test_extract_cracked_pim_colon_format():
    """:PIM=485 format should return 485."""
    line = "somehash:PIM=485:mypassword"
    assert extract_cracked_pim(line) == 485


def test_extract_cracked_pim_no_pim_returns_none():
    """Lines without PIM annotation should return None."""
    line = "somehash:mypassword"
    assert extract_cracked_pim(line) is None


def test_extract_cracked_pim_case_insensitive():
    """PIM extraction should be case-insensitive."""
    line = "$veracrypt$1$abc$def$pim=123:secret"
    assert extract_cracked_pim(line) == 123


def test_extract_cracked_pim_large_value():
    """Large PIM values should be parsed correctly."""
    line = "$veracrypt$data$PIM=9999:passphrase"
    assert extract_cracked_pim(line) == 9999


# ---------------------------------------------------------------------------
# extract_password_from_line
# ---------------------------------------------------------------------------

def test_extract_password_dollar_pim_format():
    """$PIM=485:mypassword should return 'mypassword'."""
    line = "$veracrypt$1$abc$def$PIM=485:mypassword"
    assert extract_password_from_line(line) == "mypassword"


def test_extract_password_no_pim_standard_format():
    """Standard hash:password format should return 'password'."""
    line = "somehash:password"
    assert extract_password_from_line(line) == "password"


def test_extract_password_colon_pim_format():
    """:PIM=485:secret should return 'secret'."""
    line = "somehash:PIM=485:secret"
    assert extract_password_from_line(line) == "secret"


def test_extract_password_no_colon_returns_full_line():
    """If no colon exists and no PIM, return the full line."""
    line = "nocolonhere"
    assert extract_password_from_line(line) == "nocolonhere"


def test_extract_password_empty_password():
    """Empty password after colon should return empty string."""
    line = "somehash:"
    assert extract_password_from_line(line) == ""
