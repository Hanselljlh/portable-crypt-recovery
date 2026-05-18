"""Tests for the Hashcat command builder."""

import os
from pathlib import Path

import pytest

from portable_crypt_recovery.core.ids import new_id
from portable_crypt_recovery.core.timestamps import utc_now_iso
from portable_crypt_recovery.models.header import Header
from portable_crypt_recovery.models.job import QueuedJob
from portable_crypt_recovery.services.hashcat.command_builder import (
    CommandBuilderError,
    build_command,
)
from portable_crypt_recovery.services.headers.metadata import save_header_metadata


def _make_workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "workspace"
    ws.mkdir()
    for folder in [
        "headers/metadata",
        "headers/normalized",
        "hashcat/potfile",
        "hashcat/output",
        "hashcat/logs",
        "hashcat/restore",
        "generated/wordlists",
    ]:
        (ws / folder).mkdir(parents=True)
    # Create a minimal wordlist so command_builder can validate it exists
    (ws / "generated" / "wordlists" / "test_wordlist.txt").write_text("password123\n")
    return ws


def _make_header(ws: Path) -> Header:
    header_id = new_id("header")
    normalized_path = ws / "headers" / "normalized" / f"header_{header_id}.bin"
    normalized_path.write_bytes(b"\x00" * 512)
    h = Header(
        header_id=header_id,
        target_id="target_001",
        source_type="extracted",
        workspace_relative_path=f"headers/normalized/header_{header_id}.bin",
        size_bytes=512,
        sha256="abc" * 21 + "ab",
        extraction_timestamp=utc_now_iso(),
        candidate_type="normal_volume_header",
    )
    save_header_metadata(ws, h)
    return h


def _make_job(header: Header, ws: Path) -> QueuedJob:
    job_id = new_id("job")
    session = f"pcr_{job_id}"
    return QueuedJob(
        job_id=job_id,
        target_id="target_001",
        header_id=header.header_id,
        hash_mode_set_id="modeset_001",
        pim_set_id=None,
        keyfile_set_id=None,
        password_source_id="pwsrc_001",
        status="pending",
        command_array=[],
        potfile_path=f"hashcat/potfile/{session}.potfile",
        outfile_path=f"hashcat/output/{session}.out",
        log_path=f"hashcat/logs/{session}.log",
        session_name=session,
        hashcat_mode=29411,
        pim_value=None,
        pim_mode="default",
        wordlist_path="generated/wordlists/test_wordlist.txt",
        created_timestamp=utc_now_iso(),
        updated_timestamp=utc_now_iso(),
    )


def test_command_builder_returns_list(tmp_path):
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)

    # Create a fake executable
    if os.name == "nt":
        fake_exe = tmp_path / "hashcat.cmd"
        fake_exe.write_text("@echo off\nexit /b 0\n")
    else:
        fake_exe = tmp_path / "hashcat"
        fake_exe.write_text("#!/bin/sh\nexit 0\n")
        fake_exe.chmod(0o755)

    args = build_command(job, fake_exe, ws)
    assert isinstance(args, list), "command_builder must return list[str], not a string"
    assert all(isinstance(a, str) for a in args), "All elements must be strings"


def test_command_includes_mode(tmp_path):
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)

    if os.name == "nt":
        fake_exe = tmp_path / "hashcat.cmd"
        fake_exe.write_text("@echo off\nexit /b 0\n")
    else:
        fake_exe = tmp_path / "hashcat"
        fake_exe.write_text("#!/bin/sh\nexit 0\n")
        fake_exe.chmod(0o755)

    args = build_command(job, fake_exe, ws)
    assert "-m" in args
    assert "29411" in args


def test_command_includes_potfile(tmp_path):
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)

    if os.name == "nt":
        fake_exe = tmp_path / "hashcat.cmd"
        fake_exe.write_text("@echo off\nexit /b 0\n")
    else:
        fake_exe = tmp_path / "hashcat"
        fake_exe.write_text("#!/bin/sh\nexit 0\n")
        fake_exe.chmod(0o755)

    args = build_command(job, fake_exe, ws)
    assert "--potfile-path" in args
    assert "--outfile" in args
    assert "--session" in args


def test_command_paths_are_workspace_local(tmp_path):
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)

    if os.name == "nt":
        fake_exe = tmp_path / "hashcat.cmd"
        fake_exe.write_text("@echo off\nexit /b 0\n")
    else:
        fake_exe = tmp_path / "hashcat"
        fake_exe.write_text("#!/bin/sh\nexit 0\n")
        fake_exe.chmod(0o755)

    args = build_command(job, fake_exe, ws)
    ws_str = str(ws.resolve())
    # Find all path-like args (those containing the tmp path) and check they're inside workspace
    for arg in args[1:]:  # skip executable itself
        if os.sep in arg and not arg.startswith("-") and "potfile" in arg:
            assert arg.startswith(ws_str), f"Path outside workspace: {arg}"


def test_command_pim_custom(tmp_path):
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)
    job.pim_mode = "custom"
    job.pim_value = 500

    if os.name == "nt":
        fake_exe = tmp_path / "hashcat.cmd"
        fake_exe.write_text("@echo off\nexit /b 0\n")
    else:
        fake_exe = tmp_path / "hashcat"
        fake_exe.write_text("#!/bin/sh\nexit 0\n")
        fake_exe.chmod(0o755)

    args = build_command(job, fake_exe, ws)
    assert "--veracrypt-pim-start" in args
    assert "--veracrypt-pim-stop" in args
    pim_idx = args.index("--veracrypt-pim-start")
    assert args[pim_idx + 1] == "500"


def test_command_includes_attack_mode_and_wordlist(tmp_path):
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)

    if os.name == "nt":
        fake_exe = tmp_path / "hashcat.cmd"
        fake_exe.write_text("@echo off\nexit /b 0\n")
    else:
        fake_exe = tmp_path / "hashcat"
        fake_exe.write_text("#!/bin/sh\nexit 0\n")
        fake_exe.chmod(0o755)

    args = build_command(job, fake_exe, ws)
    assert "-a" in args
    assert args[args.index("-a") + 1] == "0"
    # Wordlist path should be the last argument
    assert args[-1].endswith("test_wordlist.txt")


def test_command_fails_missing_wordlist(tmp_path):
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)
    job.wordlist_path = "generated/wordlists/nonexistent.txt"

    if os.name == "nt":
        fake_exe = tmp_path / "hashcat.cmd"
        fake_exe.write_text("@echo off\nexit /b 0\n")
    else:
        fake_exe = tmp_path / "hashcat"
        fake_exe.write_text("#!/bin/sh\nexit 0\n")
        fake_exe.chmod(0o755)

    with pytest.raises(CommandBuilderError, match="Wordlist not found"):
        build_command(job, fake_exe, ws)


def test_command_fails_missing_executable(tmp_path):
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)

    with pytest.raises(CommandBuilderError):
        build_command(job, tmp_path / "nonexistent_hashcat", ws)


def _make_keyfile_set(ws: Path, set_id: str, filenames: list[str]) -> None:
    """Write a minimal keyfile-list JSON and the dummy keyfile files."""
    import json

    kf_dir = ws / "inputs" / "keyfiles" / "normalized"
    kf_dir.mkdir(parents=True, exist_ok=True)
    kf_list_dir = ws / "generated" / "keyfile-lists"
    kf_list_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    for fn in filenames:
        rel = f"inputs/keyfiles/normalized/{fn}"
        (ws / rel).write_bytes(b"\x00" * 64)
        entries.append({
            "keyfile_id": fn.split(".")[0],
            "original_filename": fn,
            "size_bytes": 64,
            "normalized_workspace_path": rel,
            "sha256": "a" * 64,
        })
    kf_list_dir.joinpath(f"{set_id}.json").write_text(
        json.dumps({"set_id": set_id, "entries": entries}), encoding="utf-8"
    )


def _fake_exe(tmp_path: Path) -> Path:
    if os.name == "nt":
        exe = tmp_path / "hashcat.cmd"
        exe.write_text("@echo off\nexit /b 0\n")
    else:
        exe = tmp_path / "hashcat"
        exe.write_text("#!/bin/sh\nexit 0\n")
        exe.chmod(0o755)
    return exe


def test_veracrypt_mode_uses_veracrypt_keyfiles_flag(tmp_path):
    """VeraCrypt modes must use --veracrypt-keyfiles, never --keyfile."""
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)
    job.hashcat_mode = 13712  # VeraCrypt legacy
    job.keyfile_set_id = "kfset_vc"
    _make_keyfile_set(ws, "kfset_vc", ["key1.png"])

    args = build_command(job, _fake_exe(tmp_path), ws)
    assert "--veracrypt-keyfiles" in args
    assert "--truecrypt-keyfiles" not in args
    assert "--keyfile" not in args


def test_truecrypt_mode_uses_truecrypt_keyfiles_flag(tmp_path):
    """TrueCrypt modes must use --truecrypt-keyfiles, never --keyfile."""
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)
    job.hashcat_mode = 6211  # TrueCrypt legacy
    job.keyfile_set_id = "kfset_tc"
    _make_keyfile_set(ws, "kfset_tc", ["key1.png"])

    args = build_command(job, _fake_exe(tmp_path), ws)
    assert "--truecrypt-keyfiles" in args
    assert "--veracrypt-keyfiles" not in args
    assert "--keyfile" not in args


def test_multiple_keyfiles_joined_as_single_arg(tmp_path):
    """Multiple keyfiles must be comma-joined in one flag, not repeated --keyfile pairs."""
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)
    job.hashcat_mode = 29411  # VeraCrypt current
    job.keyfile_set_id = "kfset_multi"
    _make_keyfile_set(ws, "kfset_multi", ["kf_a.png", "kf_b.txt"])

    args = build_command(job, _fake_exe(tmp_path), ws)
    flag_idx = args.index("--veracrypt-keyfiles")
    kf_value = args[flag_idx + 1]
    assert "," in kf_value, "Multiple keyfiles must be comma-joined in a single value"
    assert "--keyfile" not in args


# ---------------------------------------------------------------------------
# Hash-input format: 293xx / 294xx modes need $veracrypt$/$truecrypt$ text
# ---------------------------------------------------------------------------

def _write_dummy_binary_header(ws: Path, header_id: str) -> Path:
    """Write a recognisable 512-byte binary header to the normalised dir."""
    p = ws / "headers" / "normalized" / f"header_{header_id}.bin"
    # Make it non-zero so hex output is interesting; embed 3 newlines (0x0a)
    # so we can confirm it's not mistakenly treated as multiple text lines.
    data = bytes(range(256)) * 2  # 512 bytes, deterministic
    p.write_bytes(data)
    return p


def test_legacy_vc_mode_uses_raw_binary_header(tmp_path):
    """137xx modes must receive the raw .bin file, not a text-format hash."""
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)
    job.hashcat_mode = 13711  # VeraCrypt legacy

    args = build_command(job, _fake_exe(tmp_path), ws)
    hash_input = args[5]  # exe, -a, 0, -m, MODE, <hash_input>
    assert hash_input.endswith(".bin"), f"Legacy mode should use raw .bin, got: {hash_input}"
    assert "vc_hash" not in hash_input


def test_current_vc_mode_generates_veracrypt_text_file(tmp_path):
    """294xx modes must receive a $veracrypt$salt$encrypted text file."""
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)
    job.hashcat_mode = 29411  # VeraCrypt current

    args = build_command(job, _fake_exe(tmp_path), ws)
    hash_input = args[5]  # exe, -a, 0, -m, MODE, <hash_input>
    assert hash_input.endswith(".txt"), f"294xx mode should use .txt hash file, got: {hash_input}"
    assert "vc_hash" in hash_input

    content = Path(hash_input).read_text(encoding="ascii").strip()
    assert content.startswith("$veracrypt$"), f"Expected $veracrypt$ prefix, got: {content[:30]}"
    parts = content.split("$")
    # format: '' | 'veracrypt' | salt_hex (128 chars) | enc_hex (896 chars)
    assert len(parts) == 4
    assert len(parts[2]) == 128, f"Salt hex should be 128 chars, got {len(parts[2])}"
    assert len(parts[3]) == 896, f"Encrypted hex should be 896 chars, got {len(parts[3])}"


def test_current_tc_mode_generates_truecrypt_text_file(tmp_path):
    """293xx modes must receive a $truecrypt$salt$encrypted text file."""
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)
    job.hashcat_mode = 29311  # TrueCrypt current

    args = build_command(job, _fake_exe(tmp_path), ws)
    hash_input = args[5]  # exe, -a, 0, -m, MODE, <hash_input>
    assert hash_input.endswith(".txt")
    content = Path(hash_input).read_text(encoding="ascii").strip()
    assert content.startswith("$truecrypt$"), f"Expected $truecrypt$ prefix, got: {content[:30]}"


def test_vc_hash_file_is_cached(tmp_path):
    """Calling build_command twice for the same job should reuse the same text file."""
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)
    job.hashcat_mode = 29411

    args1 = build_command(job, _fake_exe(tmp_path), ws)
    args2 = build_command(job, _fake_exe(tmp_path), ws)
    assert args1[3] == args2[3], "Hash file path should be identical on second call"
    vc_hash_dir = ws / "headers" / "vc_hash"
    files = list(vc_hash_dir.iterdir())
    assert len(files) == 1, f"Only one cached text file should exist, found: {files}"


def test_ignore_cuda_flag_added(tmp_path):
    """ignore_cuda=True must add --backend-ignore-cuda to the command."""
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)

    args = build_command(job, _fake_exe(tmp_path), ws, ignore_cuda=True)
    assert "--backend-ignore-cuda" in args


def test_ignore_cuda_off_by_default(tmp_path):
    """--backend-ignore-cuda must NOT appear when ignore_cuda is False."""
    ws = _make_workspace(tmp_path)
    header = _make_header(ws)
    job = _make_job(header, ws)

    args = build_command(job, _fake_exe(tmp_path), ws)
    assert "--backend-ignore-cuda" not in args
