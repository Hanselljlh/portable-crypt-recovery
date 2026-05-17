import pytest

from portable_crypt_recovery.services.builders.pim_builder import expand_pim_input


def test_expand_pim_range_and_dedupe():
    assert expand_pim_input("805, 789-792, 790, 485") == [485, 789, 790, 791, 792, 805]


def test_reject_zero_pim():
    with pytest.raises(ValueError):
        expand_pim_input("0")
