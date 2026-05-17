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
