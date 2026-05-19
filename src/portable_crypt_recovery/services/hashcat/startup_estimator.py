"""Hashcat startup overhead estimation and queue efficiency analysis.

The dominant cost for VeraCrypt modes is per-invocation overhead: CUDA context
creation, kernel compilation, autotune, and device warmup — typically 20–60 s.
Actual PBKDF2 compute at ~1 700 H/s (RTX 4070 Laptop) is < 1 ms per candidate.

When a job has only 1–10 candidates the startup overhead is 1 000–10 000 ×
the actual compute time.  PCR should warn users so they can use PIM range
batching or add more password candidates to amortise the fixed cost.
"""

from __future__ import annotations

from portable_crypt_recovery.models.task import QueuedTask

# Default per-invocation overhead (CUDA init + autotune + kernel warmup)
DEFAULT_STARTUP_OVERHEAD_SECONDS: int = 30

# Approximate speeds from user benchmark: hashcat v7.1.2, RTX 4070 Laptop,
# CUDA device #1, --hwmon-disable, no -O.
# All VeraCrypt/TrueCrypt 293xx/294xx modes benchmark ~1 760 H/s on this GPU.
_BENCHMARK_HPS: dict[int, int] = {
    m: 1762
    for m in [
        # VeraCrypt non-system
        29411, 29412, 29413,
        29421, 29422, 29423,
        29431, 29432, 29433,
        29451, 29452, 29453,
        29471, 29472, 29473,
        # VeraCrypt system/boot
        29441, 29442, 29443,
        29461, 29462, 29463,
        29481, 29482, 29483,
        # TrueCrypt non-system
        29311, 29312, 29313,
        29321, 29322, 29323,
        29331, 29332, 29333,
        # TrueCrypt system/boot
        29341, 29342, 29343,
    ]
}

DEFAULT_HPS: int = 1700  # conservative fallback for unknown / legacy modes


def estimate_hps(hashcat_mode: int) -> int:
    """Return H/s estimate for *hashcat_mode*."""
    return _BENCHMARK_HPS.get(hashcat_mode, DEFAULT_HPS)


def estimate_job_wall_time(
    candidate_count: int,
    hashcat_mode: int = 0,
    startup_overhead_s: int = DEFAULT_STARTUP_OVERHEAD_SECONDS,
) -> dict:
    """Estimate wall-clock time for a single Hashcat invocation.

    Returns a dict with:
      candidate_count       — input
      hps_estimate          — H/s used
      compute_seconds       — candidate_count / hps
      startup_overhead_seconds — fixed per-invocation overhead
      wall_seconds          — startup + compute
      startup_dominates     — True when startup > compute time
    """
    hps = estimate_hps(hashcat_mode)
    compute_s = candidate_count / hps if hps > 0 else 0.0
    wall_s = startup_overhead_s + compute_s
    return {
        "candidate_count": candidate_count,
        "hps_estimate": hps,
        "compute_seconds": round(compute_s, 3),
        "startup_overhead_seconds": startup_overhead_s,
        "wall_seconds": round(wall_s, 1),
        "startup_dominates": startup_overhead_s > compute_s,
    }


def pim_range_length(task: QueuedTask) -> int:
    """Number of PIM values covered by a task (1 for single-PIM or default tasks)."""
    if (
        task.pim_mode == "custom"
        and task.pim_start is not None
        and task.pim_stop is not None
    ):
        return max(1, task.pim_stop - task.pim_start + 1)
    return 1


def queue_efficiency_report(
    tasks: list[QueuedTask],
    startup_overhead_s: int = DEFAULT_STARTUP_OVERHEAD_SECONDS,
) -> dict:
    """Summarise startup-waste risk across a list of tasks.

    Uses pim_range_length as a proxy for minimum candidates per job
    (actual candidate count also depends on wordlist size which is not
    read here).

    Returns a dict with:
      total_jobs            — total task count
      small_job_count       — jobs where startup dominates
      warn                  — True when any job has startup_dominates=True
      message               — human-readable warning (empty string when warn=False)
    """
    total = len(tasks)
    small = 0
    for t in tasks:
        prl = pim_range_length(t)
        est = estimate_job_wall_time(prl, t.hashcat_mode, startup_overhead_s)
        if est["startup_dominates"]:
            small += 1

    warn = small > 0
    msg = (
        f"{small}/{total} job(s) have very small candidate counts. "
        "Hashcat startup and autotune time will dominate. "
        "Consider enabling adjacent PIM range optimisation (Settings → Hashcat) "
        "or adding more password candidates to amortise the fixed startup cost."
    ) if warn else ""

    return {
        "total_jobs": total,
        "small_job_count": small,
        "warn": warn,
        "message": msg,
    }
