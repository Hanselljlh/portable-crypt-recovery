"""Hashcat argument array builder.

Returns list[str] — never a shell string.
"""

from __future__ import annotations

from pathlib import Path

from portable_crypt_recovery.models.task import QueuedTask


class CommandBuilderError(Exception):
    pass


# ---------------------------------------------------------------------------
# Mode substitution: current → legacy when CUDA is unavailable
# ---------------------------------------------------------------------------

# The "current" VeraCrypt/TrueCrypt modes (294xx / 293xx) use a CPU bridge for
# PBKDF2 key derivation.  With CUDA available the bridge runs on the GPU
# (thousands of H/s).  With --backend-ignore-cuda the bridge falls back to a
# single CPU thread — 655 k iterations per candidate = 30–550 s per password.
#
# The legacy modes (137xx / 62xx) run the full PBKDF2+AES computation inside
# the OpenCL GPU kernel (no bridge).  They are 100–10 000× faster on OpenCL.
# This table maps each current mode to its functionally identical legacy mode.
_CURRENT_TO_LEGACY: dict[int, int] = {
    # VeraCrypt non-system
    29411: 13711, 29412: 13712, 29413: 13713,   # RIPEMD-160
    29421: 13721, 29422: 13722, 29423: 13723,   # SHA-512
    29431: 13731, 29432: 13732, 29433: 13733,   # Whirlpool
    29451: 13751, 29452: 13752, 29453: 13753,   # SHA-256
    29471: 13771, 29472: 13772, 29473: 13773,   # Streebog-512
    # VeraCrypt system/boot
    29441: 13741, 29442: 13742, 29443: 13743,   # RIPEMD-160 boot
    29461: 13761, 29462: 13762, 29463: 13763,   # SHA-256 boot
    29481: 13781, 29482: 13782, 29483: 13783,   # Streebog-512 boot
    # TrueCrypt non-system
    29311: 6211, 29312: 6212, 29313: 6213,       # RIPEMD-160
    29321: 6221, 29322: 6222, 29323: 6223,       # SHA-512
    29331: 6231, 29332: 6232, 29333: 6233,       # Whirlpool
    # TrueCrypt system/boot
    29341: 6241, 29342: 6242, 29343: 6243,       # RIPEMD-160 boot
}


# ---------------------------------------------------------------------------
# Hash-input format helpers
# ---------------------------------------------------------------------------

def _header_file_for_mode(
    workspace_root: Path,
    header_id: str,
    header_abs: Path,
    mode: int,
) -> Path:
    """Return the appropriate hash-input file path for the given hashcat mode.

    Legacy modes (137xx, 62xx) accept a raw 512-byte binary header.
    Current modes (293xx, 294xx) require a text-format hash:
      $veracrypt$<64-byte-salt-hex>$<448-byte-encrypted-hex>
      $truecrypt$<64-byte-salt-hex>$<448-byte-encrypted-hex>

    The text file is derived from the same binary header and cached in
    headers/vc_hash/ inside the workspace so it only needs to be generated once.
    """
    is_vc_current = 29411 <= mode <= 29483
    is_tc_current = 29311 <= mode <= 29343

    if not (is_vc_current or is_tc_current):
        # Legacy modes (137xx / 62xx) — raw binary, no conversion needed.
        return header_abs

    prefix = "$veracrypt$" if is_vc_current else "$truecrypt$"
    suffix = "veracrypt" if is_vc_current else "truecrypt"

    vc_hash_dir = workspace_root / "headers" / "vc_hash"
    vc_hash_dir.mkdir(parents=True, exist_ok=True)
    text_file = vc_hash_dir / f"header_{header_id}_{suffix}.txt"

    if not text_file.exists():
        raw = header_abs.read_bytes()
        if len(raw) != 512:
            raise CommandBuilderError(
                f"Header must be exactly 512 bytes (got {len(raw)}): {header_abs}"
            )
        # VeraCrypt/TrueCrypt header layout:
        #   bytes   0–63  : random salt  (64 bytes)
        #   bytes  64–511 : encrypted header area (448 bytes)
        text_file.write_text(
            f"{prefix}{raw[:64].hex()}${raw[64:].hex()}\n",
            encoding="ascii",
        )

    return text_file


# ---------------------------------------------------------------------------
# Command builders
# ---------------------------------------------------------------------------

def build_command(
    job: QueuedTask,
    hashcat_executable: Path,
    workspace_root: Path,
    use_optimized_kernels: bool = True,
    use_cpu_opencl: bool = False,
    ignore_cuda: bool = False,
) -> list[str]:
    """Build a Hashcat argument array for a QueuedTask.

    All paths are validated to be inside the workspace.
    Returns list[str] — safe for subprocess.Popen(args, ...).
    """
    from portable_crypt_recovery.core.paths import safe_join_workspace

    if not hashcat_executable.exists():
        raise CommandBuilderError(f"Hashcat executable not found: {hashcat_executable}")

    args: list[str] = [str(hashcat_executable.resolve())]

    # Attack mode: always dictionary (-a 0) for PCR jobs
    args += ["-a", "0"]

    # When CUDA is unavailable (ignore_cuda=True), "current" format modes
    # (294xx / 293xx) use a single-threaded CPU bridge for PBKDF2, making each
    # candidate 30–550 s.  Substitute the equivalent legacy mode (137xx / 62xx)
    # which runs the full PBKDF2+AES kernel on the GPU — 100–10 000× faster via
    # OpenCL.  The job record keeps its original mode; only the command changes.
    effective_mode = job.hashcat_mode
    if ignore_cuda and effective_mode in _CURRENT_TO_LEGACY:
        effective_mode = _CURRENT_TO_LEGACY[effective_mode]

    args += ["-m", str(effective_mode)]

    # Hash input — legacy modes (137xx, 62xx) use raw binary; current modes
    # (293xx, 294xx) require $veracrypt$/$truecrypt$ text format.
    # Use effective_mode so the right format is chosen after substitution.
    if not job.outfile_path:
        raise CommandBuilderError("Job has no outfile_path set.")
    from portable_crypt_recovery.services.headers.metadata import load_header_metadata
    try:
        header_meta = load_header_metadata(workspace_root, job.header_id)
        header_abs = safe_join_workspace(workspace_root, header_meta.workspace_relative_path)
    except (FileNotFoundError, ValueError) as exc:
        raise CommandBuilderError(f"Cannot resolve header path: {exc}") from exc

    hash_input = _header_file_for_mode(workspace_root, job.header_id, header_abs, effective_mode)
    args.append(str(hash_input))

    # Potfile
    potfile_abs = safe_join_workspace(workspace_root, job.potfile_path)
    args += ["--potfile-path", str(potfile_abs)]

    # Outfile
    outfile_abs = safe_join_workspace(workspace_root, job.outfile_path)
    args += ["--outfile", str(outfile_abs)]

    # Session name — used for status display only.
    # PCR manages queue state itself so we disable hashcat's own restore
    # mechanism: --restore-disable is supported by all hashcat 6.x versions
    # and avoids the --restore-file-path flag which was only added in 6.1
    # and causes "Unknown option" fatal errors on older builds.
    args += ["--session", job.session_name]
    args += ["--restore-disable"]

    # Optimized kernels: SIMD-optimized code paths, 2-4× faster.
    # Trade-off: max password length is limited to ~31 characters.
    if use_optimized_kernels:
        args += ["-O"]

    # Disable GPU hardware monitoring — avoids sensor-polling overhead and
    # driver errors on headless / virtual machines.
    args += ["--hwmon-disable"]

    # Backend flags — mutually exclusive with each other.
    # ignore_cuda: skip CUDA backend entirely; hashcat falls back to OpenCL or
    #   the built-in CPU backend.  Use when CUDA PTX version mismatch causes
    #   "Unsupported .version X.Y; current version is A.B" errors.
    # use_cpu_opencl: use OpenCL CPU device type (-D 1); requires Intel or AMD
    #   OpenCL runtime; 3-5× faster than built-in CPU.
    if ignore_cuda:
        args += ["--backend-ignore-cuda"]
    if use_cpu_opencl:
        args += ["-D", "1"]

    # Limit wordlist segment size to cap RAM usage.
    # Hashcat default loads the whole wordlist into RAM; 512 MB is a safe ceiling
    # that still allows good throughput while keeping memory pressure manageable.
    args += ["--segment-size", "512"]

    # Status output — timer=1 gives a fresh line every second so the log
    # shows real-time H/s without waiting for the default 10-second interval.
    args += ["--status", "--status-json", "--status-timer", "1"]

    # Suppress hashcat's own session .log and .pid files in the CWD (the
    # hashcat executable directory).  PCR writes its own log to the workspace;
    # having duplicate log files scattered in tools/hashcat/ is confusing.
    args += ["--logfile-disable"]

    # PIM handling
    if job.pim_mode == "custom" and job.pim_value is not None:
        args += [
            "--veracrypt-pim-start", str(job.pim_value),
            "--veracrypt-pim-stop", str(job.pim_value),
        ]

    # Keyfile handling — workspace-local keyfiles only.
    # Hashcat uses --veracrypt-keyfiles (VeraCrypt modes 13711-13783, 29411-29483)
    # and --truecrypt-keyfiles (TrueCrypt modes 6211-6243, 29311-29343).
    # Both flags accept a comma-separated list; do NOT pass --keyfile (unknown option).
    if job.keyfile_set_id:
        from portable_crypt_recovery.models.keyfile_set import KeyfileSet
        kf_set_path = workspace_root / "generated" / "keyfile-lists" / f"{job.keyfile_set_id}.json"
        if kf_set_path.exists():
            import json
            with kf_set_path.open("r", encoding="utf-8") as fh:
                kf_data = json.load(fh)
            kf_set = KeyfileSet.from_dict(kf_data)
            kf_paths = [
                str(safe_join_workspace(workspace_root, entry.normalized_workspace_path))
                for entry in kf_set.entries
            ]
            if kf_paths:
                mode = job.hashcat_mode
                is_truecrypt = (6211 <= mode <= 6243) or (29311 <= mode <= 29343)
                kf_flag = "--truecrypt-keyfiles" if is_truecrypt else "--veracrypt-keyfiles"
                args += [kf_flag, ",".join(kf_paths)]

    # Wordlist (dictionary) — must come last, positional after the hash file
    if not job.wordlist_path:
        raise CommandBuilderError("Job has no wordlist_path set. Expand the draft again.")
    wordlist_path_str = job.wordlist_path
    # Resolve workspace-relative paths; absolute paths pass through unchanged
    from pathlib import Path as _Path
    wl = _Path(wordlist_path_str)
    if not wl.is_absolute():
        wl = safe_join_workspace(workspace_root, wordlist_path_str)
    if not wl.exists():
        raise CommandBuilderError(f"Wordlist not found: {wl}")
    args.append(str(wl))

    return args


def build_command_with_devices(
    job: QueuedTask,
    hashcat_executable: Path,
    workspace_root: Path,
    device_ids: list[int] | None = None,
    use_optimized_kernels: bool = True,
    use_cpu_opencl: bool = False,
    ignore_cuda: bool = False,
) -> list[str]:
    """Build command array, appending -d device args if device_ids is specified."""
    args = build_command(
        job, hashcat_executable, workspace_root,
        use_optimized_kernels=use_optimized_kernels,
        use_cpu_opencl=use_cpu_opencl,
        ignore_cuda=ignore_cuda,
    )
    if device_ids:
        args += ["-d", ",".join(str(d) for d in device_ids)]
    return args
