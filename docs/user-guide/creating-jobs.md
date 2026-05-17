# Creating Recovery Jobs

A **job** is a single Hashcat dictionary attack run against one extracted header.
You create jobs from **drafts**, which bundle together your attack parameters.
Expanding a draft generates one or more jobs and adds them to the queue.

## Overview

```
Target -> Extract Header -> New Draft -> Expand -> Jobs in Queue -> Run Queue
```

## Step 1: Create a draft

1. Navigate to **Jobs** in the sidebar.
2. Click **New Draft**.
3. Fill in the dialog:

### Target & Header

- **Target** — the volume you want to recover
- **Header** — which extracted header to attack (normal, hidden, or system)

### Hash mode strategy

| Option | What it does |
|--------|-------------|
| Auto-detect (all modes) | Tries all applicable Hashcat modes for the selected volume family |
| VeraCrypt SHA-512 only | Mode 13721 only |
| VeraCrypt SHA-256 only | Mode 13722 only |
| TrueCrypt modes | Modes 6211–6243 |
| Specific mode | Enter one Hashcat mode number directly |

Use **Auto-detect** if you are not sure which hash algorithm was used.

### PIM (Personal Iterations Multiplier)

- **Default PIM** — standard iteration count; fastest
- **Custom PIM** — enter a specific value if you know or suspect a non-default PIM
- **PIM range** — try a range of PIM values (generates one job per value)

### Password source

- **Wordlist file** — browse to a `.txt` wordlist (one candidate per line)

### Keyfiles

If the volume uses keyfiles, click **Add Keyfile** and browse to each keyfile.
Keyfiles are stored as normalized copies inside the workspace.

## Step 2: Save and expand

After filling in the dialog, click:

- **Save Draft** — saves draft parameters without generating jobs yet
- **Save & Expand** — generates jobs immediately and adds them to the queue

You can also select a saved draft later and click **Expand Draft** to queue it.

## How many jobs are generated?

One job is created per combination of:
- hash mode (one per mode in strategy)
- PIM value (one per value in range, or just one for default/custom)
- keyfile set (one per combination, or just one if no keyfiles)

For example, Auto-detect VeraCrypt with default PIM and no keyfiles generates
approximately 4–6 jobs (one per VeraCrypt hash/cipher combination).

## Wordlist tips

- Use a targeted wordlist of likely passwords rather than a general dictionary.
- Wordlists are referenced by path; the file is not copied into the workspace.
- If you move or delete the wordlist, the jobs referencing it will fail to build.
