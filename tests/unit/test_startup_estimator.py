"""Tests for the Hashcat startup overhead estimator."""

from __future__ import annotations

from portable_crypt_recovery.models.task import QueuedTask
from portable_crypt_recovery.services.hashcat.startup_estimator import (
    DEFAULT_HPS,
    DEFAULT_STARTUP_OVERHEAD_SECONDS,
    estimate_hps,
    estimate_job_wall_time,
    queue_efficiency_report,
)


def _task(pim_start: int | None = None, pim_stop: int | None = None,
          pim_mode: str = "default", hashcat_mode: int = 29421,
          task_id: str = "task_001") -> QueuedTask:
    """Create a minimal QueuedTask for testing."""
    return QueuedTask(
        task_id=task_id,
        target_id="target_001",
        header_id="header_001",
        hash_mode_set_id="modeset_001",
        pim_set_id=None,
        keyfile_set_id=None,
        password_source_id="pwsrc_001",
        status="pending",
        command_array=[],
        potfile_path="hashcat/potfile/x.potfile",
        outfile_path="hashcat/output/x.out",
        log_path="hashcat/logs/x.log",
        session_name="pcr_x",
        hashcat_mode=hashcat_mode,
        pim_value=pim_start,
        pim_mode=pim_mode,
        pim_start=pim_start,
        pim_stop=pim_stop,
        wordlist_path="generated/wordlists/test.txt",
    )


# ---------------------------------------------------------------------------
# estimate_hps
# ---------------------------------------------------------------------------

def test_estimate_hps_known_mode():
    """Known mode 29421 should return 1762."""
    assert estimate_hps(29421) == 1762


def test_estimate_hps_unknown_mode_returns_default():
    """Unknown mode 99999 should return DEFAULT_HPS (1700)."""
    assert estimate_hps(99999) == DEFAULT_HPS
    assert DEFAULT_HPS == 1700


# ---------------------------------------------------------------------------
# estimate_job_wall_time
# ---------------------------------------------------------------------------

def test_startup_dominates_for_single_candidate():
    """1 candidate at 1762 H/s takes ~0.0006 s compute — startup dominates."""
    result = estimate_job_wall_time(1, 29421)
    assert result["startup_dominates"] is True


def test_startup_does_not_dominate_for_large_wordlist():
    """100000 candidates at 1762 H/s takes ~56.8 s compute > 30 s startup."""
    result = estimate_job_wall_time(100000, 29421)
    assert result["startup_dominates"] is False


def test_wall_seconds_equals_startup_plus_compute():
    """wall_seconds should equal startup_overhead_seconds + compute_seconds."""
    result = estimate_job_wall_time(5000, 29421, startup_overhead_s=30)
    expected = result["startup_overhead_seconds"] + result["compute_seconds"]
    assert abs(result["wall_seconds"] - round(expected, 1)) < 0.01


def test_estimate_job_wall_time_returns_all_keys():
    """Result dict must contain all expected keys."""
    result = estimate_job_wall_time(100, 29421)
    assert "candidate_count" in result
    assert "hps_estimate" in result
    assert "compute_seconds" in result
    assert "startup_overhead_seconds" in result
    assert "wall_seconds" in result
    assert "startup_dominates" in result


def test_default_startup_overhead_is_30():
    """DEFAULT_STARTUP_OVERHEAD_SECONDS should be 30."""
    assert DEFAULT_STARTUP_OVERHEAD_SECONDS == 30


# ---------------------------------------------------------------------------
# queue_efficiency_report
# ---------------------------------------------------------------------------

def test_queue_efficiency_report_empty_list():
    """Empty task list should return warn=False, total_jobs=0."""
    report = queue_efficiency_report([])
    assert report["warn"] is False
    assert report["total_jobs"] == 0
    assert report["small_job_count"] == 0
    assert report["message"] == ""


def test_queue_efficiency_report_small_tasks_warn():
    """Single-candidate tasks should trigger warn=True with non-empty message."""
    # Tasks with pim_mode="default" have pim_range_length=1 (single candidate proxy)
    tasks = [
        _task(pim_mode="default", task_id="task_a"),
        _task(pim_mode="default", task_id="task_b"),
    ]
    report = queue_efficiency_report(tasks)
    assert report["warn"] is True
    assert report["small_job_count"] > 0
    assert len(report["message"]) > 0


def test_queue_efficiency_report_large_pim_range_no_warn():
    """Tasks with a large PIM range (many candidates) should not trigger warn."""
    # pim_start=1, pim_stop=100000 → range_length=100000 → compute >> startup
    t = _task(pim_start=1, pim_stop=100000, pim_mode="custom",
              hashcat_mode=29421, task_id="task_big")
    report = queue_efficiency_report([t])
    assert report["warn"] is False


def test_queue_efficiency_report_message_format():
    """Warning message should mention the job count fraction."""
    tasks = [_task(pim_mode="default", task_id=f"task_{i}") for i in range(3)]
    report = queue_efficiency_report(tasks)
    if report["warn"]:
        assert "/" in report["message"]
        assert "job(s)" in report["message"]
