from portable_crypt_recovery.services.builders.password_builder import combine_segments


def test_combine_segments_preserves_order_and_dedupes():
    assert combine_segments([["dog", "Dog"], ["1", "1"]]) == ["dog1", "Dog1"]
