"""Tests for hashcat 7.x --backend-info parser."""

from portable_crypt_recovery.services.hashcat.device_scan import parse_backend_info

# Real hashcat 7.x --backend-info output (abbreviated)
_SAMPLE_OUTPUT = """
hashcat (v7.1.2) starting in backend information mode

Failed to initialize the AMD main driver HIP runtime library. Please install the AMD HIP SDK.

CUDA Info:
==========

CUDA.Version.: 13.1

Backend Device ID #01 (Alias: #02)
  Name...........: NVIDIA GeForce RTX 4070 Laptop GPU
  Processor(s)...: 36
  Clock..........: 1605
  Memory.Total...: 8187 MB

OpenCL Info:
============

OpenCL Platform ID #1
  Vendor..: NVIDIA Corporation
  Name....: NVIDIA CUDA

  Backend Device ID #02 (Alias: #01)
    Type...........: GPU
    Vendor.........: NVIDIA Corporation
    Name...........: NVIDIA GeForce RTX 4070 Laptop GPU
    Memory.Total...: 8187 MB

OpenCL Platform ID #2
  Vendor..: Advanced Micro Devices, Inc.

  Backend Device ID #03
    Type...........: GPU
    Vendor.........: Advanced Micro Devices, Inc.
    Name...........: AMD Radeon(TM) 610M
    Memory.Total...: 12306 MB
"""


def test_parses_three_devices():
    devices = parse_backend_info(_SAMPLE_OUTPUT)
    assert len(devices) == 3


def test_device_ids():
    devices = parse_backend_info(_SAMPLE_OUTPUT)
    ids = [d["id"] for d in devices]
    assert ids == [1, 2, 3]


def test_device_names():
    devices = parse_backend_info(_SAMPLE_OUTPUT)
    assert "RTX 4070" in devices[0]["name"]
    assert "RTX 4070" in devices[1]["name"]
    assert "610M" in devices[2]["name"]


def test_alias_cross_links():
    devices = parse_backend_info(_SAMPLE_OUTPUT)
    by_id = {d["id"]: d for d in devices}
    # CUDA #1 aliases OpenCL #2 and vice-versa
    assert by_id[1]["alias"] == 2
    assert by_id[2]["alias"] == 1
    # AMD device has no alias
    assert by_id[3]["alias"] is None


def test_label_includes_name():
    devices = parse_backend_info(_SAMPLE_OUTPUT)
    assert "RTX 4070" in devices[0]["label"]


def test_duplicate_physical_gpu_flagged():
    devices = parse_backend_info(_SAMPLE_OUTPUT)
    by_id = {d["id"]: d for d in devices}
    # Device #1 is seen first; device #2 is the OpenCL alias of the same GPU
    assert "duplicate_of" not in by_id[1]
    assert by_id[2].get("duplicate_of") == 1


def test_empty_output_returns_empty_list():
    assert parse_backend_info("") == []


def test_no_backend_device_lines_returns_empty():
    assert parse_backend_info("some random\ntext without device info\n") == []
