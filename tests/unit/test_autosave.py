"""Tests for the autosave loop."""

import json
import threading
import time

from portable_crypt_recovery.workspace.autosave import AutosaveLoop, make_queue_state_saver


def test_autosave_calls_callback(tmp_path):
    """Autosave loop calls the callback at least once."""
    call_count = [0]
    event = threading.Event()

    def callback():
        call_count[0] += 1
        event.set()

    loop = AutosaveLoop(save_callback=callback, interval_seconds=0.05)
    loop.start()
    event.wait(timeout=2.0)
    loop.stop()
    assert call_count[0] >= 1


def test_autosave_stop_prevents_further_calls(tmp_path):
    """After stop(), no more callbacks should fire."""
    call_count = [0]

    def callback():
        call_count[0] += 1

    loop = AutosaveLoop(save_callback=callback, interval_seconds=0.5)
    loop.start()
    loop.stop()
    before = call_count[0]
    time.sleep(0.6)
    after = call_count[0]
    assert after == before


def test_save_now_triggers_immediate_save(tmp_path):
    """save_now() calls the callback immediately without waiting for the timer."""
    calls = []

    def callback():
        calls.append(True)

    loop = AutosaveLoop(save_callback=callback, interval_seconds=60.0)
    loop.save_now()
    assert len(calls) == 1
    loop.stop()


def test_make_queue_state_saver_writes_file(tmp_path):
    """make_queue_state_saver returns a callable that writes queue-state.json."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    queue_dir = ws / "queue"
    queue_dir.mkdir()

    test_data = {
        "schema_version": 1, "task_order": [], "tasks": {},
        "status": "stopped", "current_running_task": None,
    }

    save_fn = make_queue_state_saver(ws, lambda: test_data)
    save_fn()

    queue_state_file = ws / "queue" / "queue-state.json"
    assert queue_state_file.exists()
    data = json.loads(queue_state_file.read_text())
    assert data["schema_version"] == 1
    assert data["status"] == "stopped"


def test_autosave_does_not_fire_while_stopped(tmp_path):
    """After stop(), timer doesn't fire more than once."""
    calls = []

    def callback():
        calls.append(True)

    loop = AutosaveLoop(save_callback=callback, interval_seconds=0.05)
    loop.start()
    time.sleep(0.1)  # Let at least one tick happen
    loop.stop()
    count_after_stop = len(calls)
    time.sleep(0.2)  # Wait for any pending ticks
    # Should not have accumulated many more
    assert len(calls) <= count_after_stop + 1  # Allow one in-flight tick
