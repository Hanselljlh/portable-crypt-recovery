"""Resume manager — removed in v0.1.33.

The stopped_saved status and Hashcat --restore-based resume were removed
because "Stop & Re-queue" resets tasks to pending instead of saving a restore
file. There is nothing to resume; the task simply re-runs from scratch.

If restore-based resume is ever needed, re-implement it here.
"""
