"""Tests for the PIM builder."""

import pytest

from portable_crypt_recovery.services.builders.pim_builder import (
    PimLimitConfirmRequired,
    PimLimitWarning,
    build_default_pim_set,
    build_pim_set,
    expand_pim_input,
)


def test_expand_pim_range_and_dedupe():
    assert expand_pim_input("805, 789-792, 790, 485") == [485, 789, 790, 791, 792, 805]


def test_reject_zero_pim():
    with pytest.raises(ValueError):
        expand_pim_input("0")


def test_reject_negative_pim():
    with pytest.raises(ValueError):
        expand_pim_input("-5")


def test_reject_invalid_range():
    with pytest.raises(ValueError):
        expand_pim_input("800-790")  # start > stop


def test_reject_empty_input():
    with pytest.raises(ValueError):
        expand_pim_input("  ")


def test_reject_non_numeric():
    with pytest.raises(ValueError):
        expand_pim_input("abc")


def test_single_value():
    assert expand_pim_input("500") == [500]


def test_range_expansion():
    assert expand_pim_input("1-3") == [1, 2, 3]


def test_dedup_sorted():
    assert expand_pim_input("5, 3, 5, 3") == [3, 5]


def test_build_pim_set_custom(tmp_path):
    ps = build_pim_set("100, 200", workspace_root=tmp_path)
    assert ps.pim_mode == "custom"
    assert ps.values == [100, 200]
    assert ps.pim_set_id.startswith("pimset_")
    # Should be saved
    pim_dir = tmp_path / "generated" / "pim-lists"
    assert any(pim_dir.glob("*.json"))


def test_build_default_pim_set():
    ps = build_default_pim_set()
    assert ps.pim_mode == "default"
    assert ps.values == []


def test_warn_above_100(tmp_path):
    values = ", ".join(str(i) for i in range(1, 102))
    with pytest.warns(PimLimitWarning):
        ps = build_pim_set(values, workspace_root=tmp_path)
    assert len(ps.values) == 101


def test_require_confirm_above_1000(tmp_path):
    values = ", ".join(str(i) for i in range(1, 1002))
    with pytest.raises(PimLimitConfirmRequired):
        build_pim_set(values, workspace_root=tmp_path)


def test_force_bypasses_confirm(tmp_path):
    values = ", ".join(str(i) for i in range(1, 1002))
    ps = build_pim_set(values, workspace_root=tmp_path, force=True)
    assert len(ps.values) == 1001
