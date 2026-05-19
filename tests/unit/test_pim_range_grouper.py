"""Tests for the PIM range grouper."""

from __future__ import annotations

from portable_crypt_recovery.models.task import QueuedTask
from portable_crypt_recovery.services.builders.pim_range_grouper import (
    group_adjacent_pim_ranges,
)


def _task(pim_value: int | None, pim_mode: str = "custom", **kwargs) -> QueuedTask:
    """Create a minimal QueuedTask for testing."""
    defaults = dict(
        task_id=f"task_{pim_value}",
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
        hashcat_mode=29421,
        pim_value=pim_value,
        pim_mode=pim_mode,
        wordlist_path="generated/wordlists/test.txt",
    )
    defaults.update(kwargs)
    return QueuedTask(**defaults)


# ---------------------------------------------------------------------------
# Adjacent PIM grouping
# ---------------------------------------------------------------------------

def test_three_adjacent_pims_grouped():
    """PIMs 485, 486, 487 should become one task with pim_start=485, pim_stop=487."""
    tasks = [_task(485), _task(486), _task(487)]
    result = group_adjacent_pim_ranges(tasks)
    assert len(result) == 1
    t = result[0]
    assert t.pim_start == 485
    assert t.pim_stop == 487


def test_non_adjacent_pims_produce_two_tasks():
    """PIMs 485,486,490,491 → two range tasks: (485–486) and (490–491)."""
    tasks = [_task(485), _task(486), _task(490), _task(491)]
    result = group_adjacent_pim_ranges(tasks)
    assert len(result) == 2
    starts = {t.pim_start for t in result}
    stops = {t.pim_stop for t in result}
    assert starts == {485, 490}
    assert stops == {486, 491}


def test_different_headers_not_combined():
    """Tasks with different header_ids must NOT be merged."""
    t1 = _task(485, header_id="header_A", task_id="task_485A")
    t2 = _task(486, header_id="header_B", task_id="task_486B")
    result = group_adjacent_pim_ranges([t1, t2])
    assert len(result) == 2


def test_different_hashcat_modes_not_combined():
    """Tasks with different hashcat_modes must NOT be merged."""
    t1 = _task(485, hashcat_mode=29421, task_id="task_485_21")
    t2 = _task(486, hashcat_mode=29422, task_id="task_486_22")
    result = group_adjacent_pim_ranges([t1, t2])
    assert len(result) == 2


def test_different_keyfile_set_ids_not_combined():
    """Tasks with different keyfile_set_ids must NOT be merged."""
    t1 = _task(485, keyfile_set_id="kfset_A", task_id="task_485_kA")
    t2 = _task(486, keyfile_set_id="kfset_B", task_id="task_486_kB")
    result = group_adjacent_pim_ranges([t1, t2])
    assert len(result) == 2


def test_different_wordlist_paths_not_combined():
    """Tasks with different wordlist_paths must NOT be merged."""
    t1 = _task(485, wordlist_path="wordlists/a.txt", task_id="task_485_wa")
    t2 = _task(486, wordlist_path="wordlists/b.txt", task_id="task_486_wb")
    result = group_adjacent_pim_ranges([t1, t2])
    assert len(result) == 2


def test_single_pim_task_unchanged():
    """A single custom-PIM task should be returned unchanged (pim_start/pim_stop=None)."""
    t = _task(500)
    result = group_adjacent_pim_ranges([t])
    assert len(result) == 1
    assert result[0] is t
    assert result[0].pim_start is None
    assert result[0].pim_stop is None


def test_default_pim_tasks_pass_through_unchanged():
    """Tasks with pim_mode='default' must pass through without modification."""
    t1 = _task(None, pim_mode="default", task_id="task_default_1")
    t2 = _task(None, pim_mode="default", task_id="task_default_2")
    result = group_adjacent_pim_ranges([t1, t2])
    assert len(result) == 2
    assert result[0].pim_start is None
    assert result[1].pim_stop is None


def test_range_start_stop_values_correct():
    """Verify pim_start and pim_stop are set to the correct boundary values."""
    tasks = [_task(10), _task(11), _task(12), _task(13)]
    result = group_adjacent_pim_ranges(tasks)
    assert len(result) == 1
    assert result[0].pim_start == 10
    assert result[0].pim_stop == 13


def test_empty_list_returns_empty():
    """Empty input returns empty output."""
    assert group_adjacent_pim_ranges([]) == []


def test_mixed_default_and_custom_pims():
    """Mix of default and custom-PIM tasks: custom ones grouped, default pass through."""
    t_default = _task(None, pim_mode="default", task_id="task_def")
    t_custom1 = _task(100, task_id="task_100")
    t_custom2 = _task(101, task_id="task_101")
    result = group_adjacent_pim_ranges([t_default, t_custom1, t_custom2])
    # 1 default + 1 merged range = 2
    assert len(result) == 2
    custom_results = [t for t in result if t.pim_mode == "custom"]
    assert len(custom_results) == 1
    assert custom_results[0].pim_start == 100
    assert custom_results[0].pim_stop == 101
