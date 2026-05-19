"""Group QueuedTask objects with adjacent custom PIM values into range tasks.

A "range task" has pim_start and pim_stop set and covers multiple adjacent PIM
values in a single Hashcat invocation:
  hashcat ... --veracrypt-pim-start 485 --veracrypt-pim-stop 490 ...

Tasks are only grouped when they share the same cracking context:
  (target_id, header_id, hashcat_mode, keyfile_set_id, wordlist_path)

Tasks with pim_mode != "custom" (i.e. default PIM) pass through unchanged.
"""

from __future__ import annotations

from copy import copy

from portable_crypt_recovery.models.task import QueuedTask


def group_adjacent_pim_ranges(tasks: list[QueuedTask]) -> list[QueuedTask]:
    """Replace tasks with adjacent custom PIMs with single range-covering tasks.

    Non-adjacent PIMs produce separate tasks (each covering one range run).
    Tasks with pim_mode != "custom" are returned unchanged.

    The first task in each adjacent run is kept as the representative task;
    its pim_start / pim_stop are updated to cover the full run.
    """
    if not tasks:
        return []

    passthrough: list[QueuedTask] = []
    custom_tasks: list[QueuedTask] = []

    for t in tasks:
        if t.pim_mode == "custom" and t.pim_value is not None:
            custom_tasks.append(t)
        else:
            passthrough.append(t)

    if not custom_tasks:
        return list(tasks)

    # Group by context key — only tasks with identical context can be batched
    groups: dict[tuple, list[QueuedTask]] = {}
    for t in custom_tasks:
        key = (
            t.target_id,
            t.header_id,
            t.hashcat_mode,
            t.keyfile_set_id or "",
            t.wordlist_path,
        )
        groups.setdefault(key, []).append(t)

    result: list[QueuedTask] = list(passthrough)
    for group_tasks in groups.values():
        # Sort ascending by PIM value so adjacency detection is correct
        group_tasks.sort(key=lambda t: t.pim_value)  # type: ignore[arg-type]
        for run in _find_adjacent_runs(group_tasks):
            result.append(_make_range_task(run))

    return result


def _find_adjacent_runs(tasks: list[QueuedTask]) -> list[list[QueuedTask]]:
    """Partition tasks into runs where consecutive pim_values are adjacent (+1)."""
    if not tasks:
        return []
    runs: list[list[QueuedTask]] = [[tasks[0]]]
    for t in tasks[1:]:
        last_val = runs[-1][-1].pim_value
        if last_val is not None and t.pim_value == last_val + 1:
            runs[-1].append(t)
        else:
            runs.append([t])
    return runs


def _make_range_task(run: list[QueuedTask]) -> QueuedTask:
    """Return a copy of the first task in a run with pim_start/pim_stop set."""
    if len(run) == 1:
        return run[0]
    merged = copy(run[0])
    merged.pim_start = run[0].pim_value
    merged.pim_stop = run[-1].pim_value
    # pim_value stays as the start value; command_builder uses pim_start/pim_stop
    return merged
