from portable_crypt_recovery.services.hashcat.device_scan import scan_devices
from portable_crypt_recovery.services.hashcat.fake_hashcat import write_fake_hashcat
from portable_crypt_recovery.services.hashcat.verifier import verify_hashcat


def test_fake_hashcat_verifies(tmp_path):
    fake = write_fake_hashcat(tmp_path / "hashcat")
    result = verify_hashcat(fake)
    assert result.ok is True
    assert result.version_text == "hashcat (fake) v0.0"


def test_fake_hashcat_device_scan(tmp_path):
    fake = write_fake_hashcat(tmp_path / "hashcat")
    result = scan_devices(fake)
    assert result.ok is True
    assert result.devices == [{"label": "Device #1", "name": "Fake CPU"}]
