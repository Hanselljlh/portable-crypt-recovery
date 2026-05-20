"""Tests for v0.2.9 named-set persistence (hash / PIM / keyfile)."""


# ---------------------------------------------------------------------------
# Hash mode set persistence
# ---------------------------------------------------------------------------

def test_save_and_list_named_hash_set(tmp_path):
    from portable_crypt_recovery.models.hash_mode_set import HashModeEntry, HashModeSet
    from portable_crypt_recovery.services.builders.hash_mode_builder import (
        list_named_hash_sets,
        save_named_hash_set,
    )

    entry = HashModeEntry(
        mode=29421,
        label="VeraCrypt SHA512 | XTS 512 bit",
        family="veracrypt",
        cipher_cascade=1,
    )
    hms = HashModeSet(mode_set_id="modeset_aabbcc", nickname="My VC Set", entries=[entry])
    save_named_hash_set(tmp_path, hms)

    sets = list_named_hash_sets(tmp_path)
    assert len(sets) == 1
    assert sets[0].nickname == "My VC Set"
    assert sets[0].mode_set_id == "modeset_aabbcc"
    assert sets[0].entries[0].mode == 29421


def test_list_named_hash_sets_sorted_by_nickname(tmp_path):
    from portable_crypt_recovery.models.hash_mode_set import HashModeEntry, HashModeSet
    from portable_crypt_recovery.services.builders.hash_mode_builder import (
        list_named_hash_sets,
        save_named_hash_set,
    )

    for nickname, mode_id in [("Zebra", "modeset_zzz"), ("Alpha", "modeset_aaa")]:
        hms = HashModeSet(
            mode_set_id=mode_id,
            nickname=nickname,
            entries=[
                HashModeEntry(mode=29421, label="x", family="veracrypt", cipher_cascade=1)
            ],
        )
        save_named_hash_set(tmp_path, hms)

    sets = list_named_hash_sets(tmp_path)
    assert [s.nickname for s in sets] == ["Alpha", "Zebra"]


def test_delete_named_hash_set(tmp_path):
    from portable_crypt_recovery.models.hash_mode_set import HashModeEntry, HashModeSet
    from portable_crypt_recovery.services.builders.hash_mode_builder import (
        delete_named_hash_set,
        list_named_hash_sets,
        save_named_hash_set,
    )

    hms = HashModeSet(
        mode_set_id="modeset_del",
        nickname="ToDelete",
        entries=[
            HashModeEntry(mode=29421, label="x", family="veracrypt", cipher_cascade=1)
        ],
    )
    save_named_hash_set(tmp_path, hms)
    assert len(list_named_hash_sets(tmp_path)) == 1

    deleted = delete_named_hash_set(tmp_path, "modeset_del")
    assert deleted is True
    assert list_named_hash_sets(tmp_path) == []


def test_delete_named_hash_set_missing_returns_false(tmp_path):
    from portable_crypt_recovery.services.builders.hash_mode_builder import (
        delete_named_hash_set,
    )

    assert delete_named_hash_set(tmp_path, "nonexistent") is False


def test_load_named_hash_set(tmp_path):
    from portable_crypt_recovery.models.hash_mode_set import HashModeEntry, HashModeSet
    from portable_crypt_recovery.services.builders.hash_mode_builder import (
        load_named_hash_set,
        save_named_hash_set,
    )

    hms = HashModeSet(
        mode_set_id="modeset_load",
        nickname="LoadMe",
        entries=[
            HashModeEntry(mode=13711, label="y", family="veracrypt", cipher_cascade=1)
        ],
    )
    save_named_hash_set(tmp_path, hms)

    loaded = load_named_hash_set(tmp_path, "modeset_load")
    assert loaded is not None
    assert loaded.nickname == "LoadMe"
    assert loaded.entries[0].mode == 13711


def test_load_named_hash_set_missing_returns_none(tmp_path):
    from portable_crypt_recovery.services.builders.hash_mode_builder import load_named_hash_set

    assert load_named_hash_set(tmp_path, "no_such_id") is None


# ---------------------------------------------------------------------------
# all_mode_entries
# ---------------------------------------------------------------------------

def test_all_mode_entries_returns_nonempty_list():
    from portable_crypt_recovery.services.builders.hash_mode_builder import all_mode_entries

    entries = all_mode_entries()
    assert len(entries) > 50


def test_all_mode_entries_no_duplicate_modes():
    from portable_crypt_recovery.services.builders.hash_mode_builder import all_mode_entries

    modes = [e.mode for e in all_mode_entries()]
    assert len(modes) == len(set(modes))


def test_all_mode_entries_families():
    from portable_crypt_recovery.services.builders.hash_mode_builder import all_mode_entries

    families = {e.family for e in all_mode_entries()}
    assert "veracrypt" in families
    assert "truecrypt" in families


# ---------------------------------------------------------------------------
# algo_from_label
# ---------------------------------------------------------------------------

def test_algo_from_label_sha512():
    from portable_crypt_recovery.services.builders.hash_mode_builder import algo_from_label

    assert algo_from_label("VeraCrypt SHA512 | XTS 512 bit") == "SHA-512"


def test_algo_from_label_ripemd():
    from portable_crypt_recovery.services.builders.hash_mode_builder import algo_from_label

    assert algo_from_label("TrueCrypt RIPEMD160 | XTS 512 bit") == "RIPEMD-160"


def test_algo_from_label_sha256():
    from portable_crypt_recovery.services.builders.hash_mode_builder import algo_from_label

    assert algo_from_label("VeraCrypt SHA256 | XTS 512 bit") == "SHA-256"


def test_algo_from_label_whirlpool():
    from portable_crypt_recovery.services.builders.hash_mode_builder import algo_from_label

    assert algo_from_label("VeraCrypt Whirlpool | XTS 512 bit") == "Whirlpool"


def test_algo_from_label_streebog():
    from portable_crypt_recovery.services.builders.hash_mode_builder import algo_from_label

    assert algo_from_label("VeraCrypt Streebog-512 | XTS 512 bit") == "Streebog-512"


# ---------------------------------------------------------------------------
# PIM set persistence
# ---------------------------------------------------------------------------

def test_save_and_list_named_pim_set(tmp_path):
    from portable_crypt_recovery.models.pim_set import PimSet
    from portable_crypt_recovery.services.builders.pim_builder import (
        list_named_pim_sets,
        save_named_pim_set,
    )

    ps = PimSet(
        pim_set_id="pimset_abc",
        nickname="High PIM",
        pim_mode="custom",
        values=[500, 501, 502],
    )
    save_named_pim_set(tmp_path, ps)

    sets = list_named_pim_sets(tmp_path)
    assert len(sets) == 1
    assert sets[0].nickname == "High PIM"
    assert sets[0].values == [500, 501, 502]


def test_list_named_pim_sets_sorted_by_nickname(tmp_path):
    from portable_crypt_recovery.models.pim_set import PimSet
    from portable_crypt_recovery.services.builders.pim_builder import (
        list_named_pim_sets,
        save_named_pim_set,
    )

    for nickname, pim_id in [("Zebra", "pimset_zzz"), ("Alpha", "pimset_aaa")]:
        save_named_pim_set(tmp_path, PimSet(pim_set_id=pim_id, nickname=nickname))

    sets = list_named_pim_sets(tmp_path)
    assert [s.nickname for s in sets] == ["Alpha", "Zebra"]


def test_delete_named_pim_set(tmp_path):
    from portable_crypt_recovery.models.pim_set import PimSet
    from portable_crypt_recovery.services.builders.pim_builder import (
        delete_named_pim_set,
        list_named_pim_sets,
        save_named_pim_set,
    )

    save_named_pim_set(tmp_path, PimSet(pim_set_id="pimset_del", nickname="Del"))
    assert len(list_named_pim_sets(tmp_path)) == 1

    assert delete_named_pim_set(tmp_path, "pimset_del") is True
    assert list_named_pim_sets(tmp_path) == []


def test_delete_named_pim_set_missing_returns_false(tmp_path):
    from portable_crypt_recovery.services.builders.pim_builder import delete_named_pim_set

    assert delete_named_pim_set(tmp_path, "no_such") is False


def test_load_named_pim_set(tmp_path):
    from portable_crypt_recovery.models.pim_set import PimSet
    from portable_crypt_recovery.services.builders.pim_builder import (
        load_named_pim_set,
        save_named_pim_set,
    )

    save_named_pim_set(
        tmp_path,
        PimSet(pim_set_id="pimset_load", nickname="LoadMe", pim_mode="custom", values=[485]),
    )

    loaded = load_named_pim_set(tmp_path, "pimset_load")
    assert loaded is not None
    assert loaded.values == [485]


def test_load_named_pim_set_missing_returns_none(tmp_path):
    from portable_crypt_recovery.services.builders.pim_builder import load_named_pim_set

    assert load_named_pim_set(tmp_path, "no_such") is None


# ---------------------------------------------------------------------------
# Keyfile set persistence
# ---------------------------------------------------------------------------

def test_save_and_list_named_keyfile_set(tmp_path):
    from portable_crypt_recovery.models.keyfile_set import KeyfileEntry, KeyfileSet
    from portable_crypt_recovery.services.builders.keyfile_builder import (
        list_named_keyfile_sets,
        save_named_keyfile_set,
    )

    entry = KeyfileEntry(
        keyfile_id="keyfile_abc",
        original_path="/orig/key.bin",
        normalized_workspace_path="inputs/keyfiles/normalized/keyfile_abc.bin",
        size_bytes=1024,
        sha256="abcd1234",
    )
    ks = KeyfileSet(set_id="kfset_abc", nickname="My Keys", entries=[entry])
    save_named_keyfile_set(tmp_path, ks)

    sets = list_named_keyfile_sets(tmp_path)
    assert len(sets) == 1
    assert sets[0].nickname == "My Keys"
    assert sets[0].entries[0].keyfile_id == "keyfile_abc"


def test_list_named_keyfile_sets_sorted_by_nickname(tmp_path):
    from portable_crypt_recovery.models.keyfile_set import KeyfileSet
    from portable_crypt_recovery.services.builders.keyfile_builder import (
        list_named_keyfile_sets,
        save_named_keyfile_set,
    )

    for nickname, sid in [("Zebra", "kfset_zzz"), ("Alpha", "kfset_aaa")]:
        save_named_keyfile_set(tmp_path, KeyfileSet(set_id=sid, nickname=nickname))

    sets = list_named_keyfile_sets(tmp_path)
    assert [s.nickname for s in sets] == ["Alpha", "Zebra"]


def test_delete_named_keyfile_set(tmp_path):
    from portable_crypt_recovery.models.keyfile_set import KeyfileSet
    from portable_crypt_recovery.services.builders.keyfile_builder import (
        delete_named_keyfile_set,
        list_named_keyfile_sets,
        save_named_keyfile_set,
    )

    save_named_keyfile_set(tmp_path, KeyfileSet(set_id="kfset_del", nickname="Del"))
    assert len(list_named_keyfile_sets(tmp_path)) == 1

    assert delete_named_keyfile_set(tmp_path, "kfset_del") is True
    assert list_named_keyfile_sets(tmp_path) == []


def test_delete_named_keyfile_set_missing_returns_false(tmp_path):
    from portable_crypt_recovery.services.builders.keyfile_builder import (
        delete_named_keyfile_set,
    )

    assert delete_named_keyfile_set(tmp_path, "no_such") is False


def test_load_named_keyfile_set(tmp_path):
    from portable_crypt_recovery.models.keyfile_set import KeyfileEntry, KeyfileSet
    from portable_crypt_recovery.services.builders.keyfile_builder import (
        load_named_keyfile_set,
        save_named_keyfile_set,
    )

    ks = KeyfileSet(
        set_id="kfset_load",
        nickname="LoadMe",
        entries=[
            KeyfileEntry(
                keyfile_id="kf1",
                original_path="/orig/a.bin",
                normalized_workspace_path="inputs/keyfiles/normalized/kf1.bin",
                size_bytes=512,
                sha256="deadbeef",
            )
        ],
    )
    save_named_keyfile_set(tmp_path, ks)

    loaded = load_named_keyfile_set(tmp_path, "kfset_load")
    assert loaded is not None
    assert loaded.nickname == "LoadMe"
    assert loaded.entries[0].sha256 == "deadbeef"


def test_load_named_keyfile_set_missing_returns_none(tmp_path):
    from portable_crypt_recovery.services.builders.keyfile_builder import (
        load_named_keyfile_set,
    )

    assert load_named_keyfile_set(tmp_path, "no_such") is None


# ---------------------------------------------------------------------------
# HashModeSet nickname round-trip
# ---------------------------------------------------------------------------

def test_hash_mode_set_nickname_roundtrip():
    from portable_crypt_recovery.models.hash_mode_set import HashModeEntry, HashModeSet

    hms = HashModeSet(
        mode_set_id="modeset_rt",
        nickname="Round Trip",
        entries=[
            HashModeEntry(mode=29421, label="x", family="veracrypt", cipher_cascade=1)
        ],
    )
    d = hms.to_dict()
    assert d["nickname"] == "Round Trip"
    hms2 = HashModeSet.from_dict(d)
    assert hms2.nickname == "Round Trip"


def test_pim_set_nickname_roundtrip():
    from portable_crypt_recovery.models.pim_set import PimSet

    ps = PimSet(pim_set_id="pimset_rt", nickname="RT PIM", pim_mode="custom", values=[100])
    d = ps.to_dict()
    assert d["nickname"] == "RT PIM"
    assert PimSet.from_dict(d).nickname == "RT PIM"


def test_keyfile_set_nickname_roundtrip():
    from portable_crypt_recovery.models.keyfile_set import KeyfileSet

    ks = KeyfileSet(set_id="kfset_rt", nickname="RT KF")
    d = ks.to_dict()
    assert d["nickname"] == "RT KF"
    assert KeyfileSet.from_dict(d).nickname == "RT KF"


# ---------------------------------------------------------------------------
# hash_set_from_hints — auto-link wizard → Hash Set
# ---------------------------------------------------------------------------

def test_hash_set_from_hints_returns_none_when_no_hints(tmp_path):
    from portable_crypt_recovery.services.builders.hash_mode_builder import hash_set_from_hints

    assert hash_set_from_hints(tmp_path, [], [], "empty") is None


def test_hash_set_from_hints_creates_set_for_kdf_hint(tmp_path):
    from portable_crypt_recovery.services.builders.hash_mode_builder import (
        hash_set_from_hints,
        list_named_hash_sets,
    )

    hms = hash_set_from_hints(tmp_path, ["sha512"], [], "SHA-512 only")
    assert hms is not None
    assert len(hms.entries) > 0
    # All entries must be SHA-512
    assert all("SHA512" in e.label or "SHA-512" in e.label for e in hms.entries)
    # Persisted
    assert len(list_named_hash_sets(tmp_path)) == 1


def test_hash_set_from_hints_filters_xts_size(tmp_path):
    from portable_crypt_recovery.services.builders.hash_mode_builder import hash_set_from_hints

    hms = hash_set_from_hints(tmp_path, [], [512], "Single cipher only")
    assert hms is not None
    # All entries must be XTS 512
    assert all("XTS 512" in e.label for e in hms.entries)
    assert all(e.cipher_cascade == 1 for e in hms.entries)


def test_hash_set_from_hints_combined_filter(tmp_path):
    from portable_crypt_recovery.services.builders.hash_mode_builder import hash_set_from_hints

    hms = hash_set_from_hints(tmp_path, ["ripemd160"], [512], "RIPEMD-160 single")
    assert hms is not None
    assert all("RIPEMD160" in e.label for e in hms.entries)
    assert all(e.cipher_cascade == 1 for e in hms.entries)


def test_hash_set_from_hints_uses_nickname(tmp_path):
    from portable_crypt_recovery.services.builders.hash_mode_builder import hash_set_from_hints

    hms = hash_set_from_hints(tmp_path, ["sha512"], [], "My custom name")
    assert hms is not None
    assert hms.nickname == "My custom name"


# ---------------------------------------------------------------------------
# Header model — suggested_mode_set_id round-trip
# ---------------------------------------------------------------------------

def test_header_suggested_mode_set_id_roundtrip():
    from portable_crypt_recovery.models.header import Header

    h = Header(
        header_id="hdr1",
        target_id="tgt1",
        source_type="extracted",
        workspace_relative_path="headers/normalized/hdr1.bin",
        size_bytes=512,
        sha256="abcd",
        extraction_timestamp="2026-01-01T00:00:00Z",
        suggested_mode_set_id="modeset_xyz",
    )
    d = h.to_dict()
    assert d["suggested_mode_set_id"] == "modeset_xyz"
    h2 = Header.from_dict(d)
    assert h2.suggested_mode_set_id == "modeset_xyz"


def test_header_suggested_mode_set_id_defaults_empty():
    from portable_crypt_recovery.models.header import Header

    h = Header(
        header_id="hdr2",
        target_id="tgt1",
        source_type="extracted",
        workspace_relative_path="headers/normalized/hdr2.bin",
        size_bytes=512,
        sha256="abcd",
        extraction_timestamp="2026-01-01T00:00:00Z",
    )
    assert h.suggested_mode_set_id == ""
    # Old JSON without the field defaults gracefully
    d = {k: v for k, v in h.to_dict().items() if k != "suggested_mode_set_id"}
    h2 = Header.from_dict(d)
    assert h2.suggested_mode_set_id == ""


# ---------------------------------------------------------------------------
# SCREEN_NAMES includes the three new screens
# ---------------------------------------------------------------------------

def test_screen_names_include_new_set_screens():
    from portable_crypt_recovery.ui.main_window import SCREEN_NAMES

    assert "Hash Sets" in SCREEN_NAMES
    assert "PIM Sets" in SCREEN_NAMES
    assert "Keyfile Sets" in SCREEN_NAMES


def test_screen_names_order():
    from portable_crypt_recovery.ui.main_window import SCREEN_NAMES

    names = list(SCREEN_NAMES)
    assert names.index("Hash Sets") < names.index("Jobs")
    assert names.index("PIM Sets") < names.index("Jobs")
    assert names.index("Keyfile Sets") < names.index("Jobs")
