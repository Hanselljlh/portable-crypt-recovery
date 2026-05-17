# Running the Queue

The **Queue** view lets you start, pause, resume, and stop the recovery queue.
Jobs run one at a time in the order they were added.

## Before you start

Make sure:
1. A workspace is open (Settings → Workspace)
2. Hashcat is configured and verified (Settings → Hashcat Setup)
3. At least one pending job exists in the queue

## Starting the queue

1. Navigate to **Queue** in the sidebar.
2. Click **Start Queue**.

PCR will run each pending job one at a time, updating the job list as statuses
change. The progress bar and status label update every two seconds.

## Queue controls

| Button | What it does |
|--------|-------------|
| Start Queue | Begin running all pending jobs |
| Pause Now | Suspend the current Hashcat process immediately |
| Pause After Current | Let the current job finish, then pause |
| Resume | Resume a paused job |
| Stop & Save | Terminate the current job, mark it `stopped_saved` |
| Stop & Discard | Terminate the current job, mark it `failed` |
| Skip Selected | Mark the selected job as `skipped` (will not run) |
| Restart Selected | Reset the selected job back to `pending` |

## Job status colors

| Color | Status | Meaning |
|-------|--------|---------|
| White | pending | Waiting to run |
| Green | running | Currently executing |
| Green | cracked | Password recovered |
| Yellow | paused / stopped_saved | Suspended or saved mid-run |
| Red | exhausted | Wordlist exhausted, no match |
| Red | failed | Unexpected error or discarded |
| Grey | skipped | Manually skipped |

## What happens when a password is found?

When Hashcat recovers a password:

1. The job is marked `cracked`.
2. A report package is automatically created in `reports/cracked/`.
3. Depending on your **behavior after crack** setting (Settings → Preferences):
   - **Continue** — the queue keeps running remaining jobs
   - **Stop entire queue** — the queue stops after the cracked job

See [Reports](reports.md) to view and export recovery packages.

## Lock file

PCR writes a lock file (`queue/runner-lock.json`) when the queue is running.
This prevents two instances of PCR from running the same queue simultaneously.
If the app crashes while the queue is active, you may see a prompt on the next
startup offering to remove the stale lock.

## Resume after crash

Jobs that were `running` when the app crashed are left in `running` status.
Use **Restart Selected** to reset them to `pending` before starting the queue again.
