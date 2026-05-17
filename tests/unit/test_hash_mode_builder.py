"""Tests for the hash mode builder."""

from portable_crypt_recovery.services.builders.hash_mode_builder import (
    build_mode_set,
    system_modes,
    truecrypt_only_modes,
    try_all_valid,
    veracrypt_only_modes,
)


def test_truecrypt_nonsystem_modes_are_valid():
    ms = build_mode_set("truecrypt", "normal_volume_header")
    modes = {e.mode for e in ms.entries}
    # All entries should be truecrypt family
    assert all(e.family == "truecrypt" for e in ms.entries)
    # Should have entries
    assert len(ms.entries) > 0


def test_truecrypt_does_not_get_veracrypt_only_modes():
    """TrueCrypt mode set must not include VeraCrypt-only mode numbers."""
    ms = build_mode_set("truecrypt", "normal_volume_header")
    tc_mode_numbers = {e.mode for e in ms.entries}
    vc_only = veracrypt_only_modes()
    # No overlap between TrueCrypt results and VeraCrypt-only modes
    assert tc_mode_numbers.isdisjoint(vc_only), (
        f"TrueCrypt mode set contains VeraCrypt-only modes: {tc_mode_numbers & vc_only}"
    )


def test_veracrypt_does_not_get_truecrypt_only_modes():
    """VeraCrypt mode set must not include TrueCrypt-only mode numbers."""
    ms = build_mode_set("veracrypt", "normal_volume_header")
    vc_mode_numbers = {e.mode for e in ms.entries}
    tc_only = truecrypt_only_modes()
    assert vc_mode_numbers.isdisjoint(tc_only), (
        f"VeraCrypt mode set contains TrueCrypt-only modes: {vc_mode_numbers & tc_only}"
    )


def test_system_modes_only_for_system_header():
    """System headers get system/boot modes; non-system headers do not."""
    sys_ms = build_mode_set("veracrypt", "normal_system_header")
    nonsys_ms = build_mode_set("veracrypt", "normal_volume_header")

    sys_mode_nums = {e.mode for e in sys_ms.entries}
    nonsys_mode_nums = {e.mode for e in nonsys_ms.entries}
    boot_modes = system_modes()

    # System header should only have system modes
    assert sys_mode_nums.issubset(boot_modes), (
        f"System header set has non-boot modes: {sys_mode_nums - boot_modes}"
    )
    # Non-system header should have no system modes
    assert nonsys_mode_nums.isdisjoint(boot_modes), (
        f"Non-system header set has boot modes: {nonsys_mode_nums & boot_modes}"
    )


def test_both_family_includes_veracrypt_and_truecrypt():
    ms = build_mode_set("both", "normal_volume_header")
    families = {e.family for e in ms.entries}
    assert "veracrypt" in families
    assert "truecrypt" in families


def test_try_all_valid_returns_mode_set():
    ms = try_all_valid("both", "normal_volume_header")
    assert ms.mode_set_id.startswith("modeset_")
    assert len(ms.entries) > 0


def test_supported_modes_filter():
    """When supported_modes is provided, only those modes are included."""
    # Only include mode 29411
    supported = {29411: "VeraCrypt RIPEMD160 + XTS 512 bit"}
    ms = build_mode_set("veracrypt", "normal_volume_header", supported_modes=supported)
    modes = [e.mode for e in ms.entries]
    assert modes == [29411]


def test_mode_set_id_unique():
    ms1 = build_mode_set("veracrypt", "normal_volume_header")
    ms2 = build_mode_set("veracrypt", "normal_volume_header")
    assert ms1.mode_set_id != ms2.mode_set_id


def test_hidden_volume_uses_nonsystem_modes():
    ms = build_mode_set("veracrypt", "hidden_volume_header")
    modes = {e.mode for e in ms.entries}
    boot_modes = system_modes()
    assert modes.isdisjoint(boot_modes)
