"""Hashcat argument array builder.

Returns list[str] — never a shell string.
"""

from __future__ import annotations

from pathlib import Path

from portable_crypt_recovery.models.job import QueuedJob


class CommandBuilderError(Exception):
    pass


def build_command(
    job: QueuedJob,
    hashcat_executable: Path,
    workspace_root: Path,
    use_optimized_kernels: bool = True,
    use_cpu_opencl: bool = False,
) -> list[str]:
    """Build a Hashcat argument array for a QueuedJob.

    All paths are validated to be inside the workspace.
    Returns list[str] — safe for subprocess.Popen(args, ...).
    """
    from portable_crypt_recovery.core.paths import safe_join_workspace

    if not hashcat_executable.exists():
        raise CommandBuilderError(f"Hashcat executable not found: {hashcat_executable}")

    args: list[str] = [str(hashcat_executable.resolve())]

    # Attack mode: always dictionary (-a 0) for PCR jobs
    args += ["-a", "0"]

    # Hash mode
    args += ["-m", str(job.hashcat_mode)]

    # Hash input: 512-byte normalized header
    if not job.outfile_path:
        raise CommandBuilderError("Job has no outfile_path set.")
    from portable_crypt_recovery.services.headers.metadata import load_header_metadata
    try:
        header_meta = load_header_metadata(workspace_root, job.header_id)
        header_abs = safe_join_workspace(workspace_root, header_meta.workspace_relative_path)
    except (FileNotFoundError, ValueError) as exc:
        raise CommandBuilderError(f"Cannot resolve header path: {exc}") from exc

    args.append(str(header_abs))

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

    # CPU OpenCL backend: -D 1 tells hashcat to use the OpenCL CPU device type
    # instead of its built-in pure-CPU path. Requires the Intel or AMD OpenCL
    # runtime to be installed; can be 3-5× faster than the default CPU backend.
    if use_cpu_opencl:
        args += ["-D", "1"]

    # Limit wordlist segment size to cap RAM usage.
    # Hashcat default loads the whole wordlist into RAM; 512 MB is a safe ceiling
    # that still allows good throughput while keeping memory pressure manageable.
    args += ["--segment-size", "512"]

    # Status output — timer=1 gives a fresh line every second so the log
    # shows real-time H/s without waiting for the default 10-second interval.
    args += ["--status", "--status-json", "--status-timer", "1"]

    # Device selection
    if job.pim_set_id is not None:
        # device args come from hashcat_setup; not available here — callers should inject
        pass

    # PIM handling
    if job.pim_mode == "custom" and job.pim_value is not None:
        args += [
            "--veracrypt-pim-start", str(job.pim_value),
            "--veracrypt-pim-stop", str(job.pim_value),
        ]

    # Keyfile handling — workspace-local keyfiles only
    if job.keyfile_set_id:
        from portable_crypt_recovery.models.keyfile_set import KeyfileSet
        kf_set_path = workspace_root / "generated" / "keyfile-lists" / f"{job.keyfile_set_id}.json"
        if kf_set_path.exists():
            import json
            with kf_set_path.open("r", encoding="utf-8") as fh:
                kf_data = json.load(fh)
            kf_set = KeyfileSet.from_dict(kf_data)
            for entry in kf_set.entries:
                kf_abs = safe_join_workspace(workspace_root, entry.normalized_workspace_path)
                args += ["--keyfile", str(kf_abs)]

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
    job: QueuedJob,
    hashcat_executable: Path,
    workspace_root: Path,
    device_ids: list[int] | None = None,
    use_optimized_kernels: bool = True,
    use_cpu_opencl: bool = False,
) -> list[str]:
    """Build command array, appending -d device args if device_ids is specified."""
    args = build_command(
        job, hashcat_executable, workspace_root,
        use_optimized_kernels=use_optimized_kernels,
        use_cpu_opencl=use_cpu_opencl,
    )
    if device_ids:
        args += ["-d", ",".join(str(d) for d in device_ids)]
    return args
