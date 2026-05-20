"""Tests for the five targeted v0.2.6 bug fixes.

Fix 1 — setup_view crash: HashcatSetup.hashcat_path → executable_path
Fix 2 — queue dedup too coarse: key now includes wordlist/PIM/keyfile
Fix 3 — eager expansion guards: estimate before generating, not after
Fix 4 — default selected_device_ids was [1]; now []
Fix 5 — "aborted" missing from JOB_STATUSES declaration
"""

from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# Fix 1 — HashcatSetup attribute name
# ---------------------------------------------------------------------------


def test_hashcat_setup_has_executable_path():
    from portable_crypt_recovery.models.hashcat_setup import HashcatSetup

    hs = HashcatSetup(executable_path="/usr/bin/hashcat")
    assert hs.executable_path == "/usr/bin/hashcat"


def test_hashcat_setup_has_no_hashcat_path_attribute():
    from portable_crypt_recovery.models.hashcat_setup import HashcatSetup

    hs = HashcatSetup()
    assert not hasattr(hs, "hashcat_path"), (
        "HashcatSetup must not expose 'hashcat_path'; setup_view must use 'executable_path'"
    )


def test_app_state_is_hashcat_ready_uses_executable_path():
    from portable_crypt_recovery.app.app_state import AppState
    from portable_crypt_recovery.models.hashcat_setup import HashcatSetup

    state = AppState()
    state.hashcat_setup = HashcatSetup(executable_path="/bin/hashcat", verified=True)
    assert state.is_hashcat_ready()

    state.hashcat_setup = HashcatSetup(executable_path=None, verified=False)
    assert not state.is_hashcat_ready()


# ---------------------------------------------------------------------------
# Fix 2 — Queue deduplication key includes all command-affecting fields
# ---------------------------------------------------------------------------


def _run_dedup(tasks, ignore_cuda=False):
    """Replicate the dedup loop from queue_view._start_queue and return skipped ids."""
    from portable_crypt_recovery.services.hashcat.command_builder import _CURRENT_TO_LEGACY

    seen_exact: set[tuple] = set()
    skipped = []
    for task in tasks:
        eff_mode = (
            _CURRENT_TO_LEGACY.get(task.hashcat_mode, task.hashcat_mode)
            if ignore_cuda
            else task.hashcat_mode
        )
        key = (
            task.header_id,
            eff_mode,
            task.wordlist_path,
            task.keyfile_set_id,
            task.pim_mode,
            task.pim_value,
            task.pim_start,
            task.pim_stop,
        )
        if key in seen_exact:
            skipped.append(task.task_id)
            continue
        seen_exact.add(key)
    return skipped


def _make_task(task_id, header_id="hdr1", mode=29421, wordlist="wl.txt",
               keyfile_set_id=None, pim_mode="default",
               pim_value=None, pim_start=None, pim_stop=None):
    from portable_crypt_recovery.models.task import QueuedTask

    return QueuedTask(
        task_id=task_id,
        target_id="tgt1",
        header_id=header_id,
        hash_mode_set_id="",
        pim_set_id=None,
        keyfile_set_id=keyfile_set_id,
        password_source_id="",
        status="pending",
        command_array=[],
        potfile_path="",
        outfile_path="out.txt",
        log_path="",
        session_name=f"s_{task_id}",
        hashcat_mode=mode,
        wordlist_path=wordlist,
        pim_mode=pim_mode,
        pim_value=pim_value,
        pim_start=pim_start,
        pim_stop=pim_stop,
    )


def test_dedup_different_wordlists_not_skipped():
    """Same header+mode but different wordlist = distinct attack, must not skip."""
    tasks = [
        _make_task("t1", wordlist="list_a.txt"),
        _make_task("t2", wordlist="list_b.txt"),
    ]
    assert _run_dedup(tasks) == []


def test_dedup_different_keyfiles_not_skipped():
    tasks = [
        _make_task("t1", keyfile_set_id="kf_set_1"),
        _make_task("t2", keyfile_set_id="kf_set_2"),
    ]
    assert _run_dedup(tasks) == []


def test_dedup_different_pim_values_not_skipped():
    tasks = [
        _make_task("t1", pim_mode="custom", pim_value=100),
        _make_task("t2", pim_mode="custom", pim_value=200),
    ]
    assert _run_dedup(tasks) == []


def test_dedup_different_pim_ranges_not_skipped():
    tasks = [
        _make_task("t1", pim_mode="custom", pim_start=100, pim_stop=150),
        _make_task("t2", pim_mode="custom", pim_start=151, pim_stop=200),
    ]
    assert _run_dedup(tasks) == []


def test_dedup_exact_duplicate_is_skipped():
    """Two tasks identical in every command-affecting field must deduplicate."""
    tasks = [
        _make_task("t1"),
        _make_task("t2"),  # same defaults as t1
    ]
    assert _run_dedup(tasks) == ["t2"]


def test_dedup_different_headers_not_skipped():
    tasks = [
        _make_task("t1", header_id="hdr_a"),
        _make_task("t2", header_id="hdr_b"),
    ]
    assert _run_dedup(tasks) == []


def test_dedup_different_modes_not_skipped():
    tasks = [
        _make_task("t1", mode=29421),
        _make_task("t2", mode=29422),
    ]
    assert _run_dedup(tasks) == []


# ---------------------------------------------------------------------------
# Fix 3 — Estimation helpers are cheap and accurate
# ---------------------------------------------------------------------------


def test_estimate_qc_no_token():
    from portable_crypt_recovery.services.builders.password_builder import (
        estimate_qc_expansion_count,
    )

    assert estimate_qc_expansion_count("hello") == 1


def test_estimate_qc_one_token():
    from portable_crypt_recovery.services.builders.password_builder import (
        estimate_qc_expansion_count,
    )

    assert estimate_qc_expansion_count("pa?Cs") == 52


def test_estimate_qc_two_tokens():
    from portable_crypt_recovery.services.builders.password_builder import (
        estimate_qc_expansion_count,
    )

    assert estimate_qc_expansion_count("?C?C") == 52 * 52


def test_estimate_qc_large_does_not_allocate():
    """5 tokens = 52^5 = 380 M — estimate must return instantly without expansion."""
    from portable_crypt_recovery.services.builders.password_builder import (
        estimate_qc_expansion_count,
    )

    assert estimate_qc_expansion_count("?C?C?C?C?C") == 52 ** 5


def test_estimate_qc_matches_actual_expansion():
    """Estimate must equal len(expand_pattern_tokens(text)) for small inputs."""
    from portable_crypt_recovery.services.builders.password_builder import (
        estimate_qc_expansion_count,
        expand_pattern_tokens,
    )

    for pattern in ["?C", "pa?Cs", "?C?C"]:
        assert estimate_qc_expansion_count(pattern) == len(expand_pattern_tokens(pattern))


def test_estimate_perm_basic():
    from portable_crypt_recovery.services.builders.password_builder import (
        estimate_permutation_count,
    )

    assert estimate_permutation_count("abc") == math.factorial(3)


def test_estimate_perm_large_does_not_allocate():
    """12-char word = 12! = 479 M — estimate returns instantly without expanding."""
    from portable_crypt_recovery.services.builders.password_builder import (
        estimate_permutation_count,
    )

    assert estimate_permutation_count("abcdefghijkl") == math.factorial(12)


def test_estimate_perm_upper_bound_for_dedup_words():
    """Estimate is an upper bound; repeated chars reduce the real count but not estimate."""
    from portable_crypt_recovery.services.builders.password_builder import (
        estimate_permutation_count,
        permutation_variants,
    )

    # "aa" has 1 unique permutation but estimate = 2! = 2
    assert estimate_permutation_count("aa") == math.factorial(2)
    assert len(permutation_variants("aa")) == 1


# ---------------------------------------------------------------------------
# Fix 4 — Default device IDs are now empty
# ---------------------------------------------------------------------------


def test_hashcat_setup_default_device_ids_empty():
    from portable_crypt_recovery.models.hashcat_setup import HashcatSetup

    assert HashcatSetup().selected_device_ids == []


def test_hashcat_setup_from_dict_no_key_gives_empty():
    from portable_crypt_recovery.models.hashcat_setup import HashcatSetup

    assert HashcatSetup.from_dict({}).selected_device_ids == []


def test_empty_device_ids_evaluates_falsy_for_queue():
    """queue_view does `device_ids = hs.selected_device_ids or None`.
    Empty list must evaluate falsy so device_ids becomes None and -d is not appended."""
    from portable_crypt_recovery.models.hashcat_setup import HashcatSetup

    hs = HashcatSetup()
    device_ids = hs.selected_device_ids or None
    assert device_ids is None


def test_explicit_device_ids_still_work():
    from portable_crypt_recovery.models.hashcat_setup import HashcatSetup

    hs = HashcatSetup(selected_device_ids=[1, 2])
    device_ids = hs.selected_device_ids or None
    assert device_ids == [1, 2]


def test_hashcat_setup_from_dict_explicit_ids_preserved():
    from portable_crypt_recovery.models.hashcat_setup import HashcatSetup

    hs = HashcatSetup.from_dict({"selected_device_ids": [2, 3]})
    assert hs.selected_device_ids == [2, 3]


# ---------------------------------------------------------------------------
# Fix 5 — "aborted" declared in JOB_STATUSES
# ---------------------------------------------------------------------------


def test_aborted_in_job_statuses():
    from portable_crypt_recovery.models.task import JOB_STATUSES

    assert "aborted" in JOB_STATUSES


def test_all_runtime_statuses_declared():
    from portable_crypt_recovery.models.task import JOB_STATUSES

    runtime = {
        "pending", "running", "paused", "cracked",
        "exhausted", "failed", "skipped", "aborted",
    }
    assert runtime <= set(JOB_STATUSES), (
        f"Missing from JOB_STATUSES: {runtime - set(JOB_STATUSES)}"
    )
