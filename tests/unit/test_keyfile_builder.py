from portable_crypt_recovery.services.builders.keyfile_builder import KEYFILE_USED_BYTES_LIMIT, normalize_keyfile


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
