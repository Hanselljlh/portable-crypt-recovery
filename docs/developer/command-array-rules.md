# Command Array Rules

## Rule: Always Use Argument Lists

All Hashcat subprocess invocations MUST use a Python list of strings, never a shell string.

### Correct

```python
args = [
    str(hashcat_executable),
    "-m", "29411",
    str(header_path),
    "--potfile-path", str(potfile_path),
    "--outfile", str(outfile_path),
    "--session", session_name,
    "--status",
    "--status-json",
]
subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
```

### Never Do This

```python
# WRONG — shell injection risk, banned
cmd = f"hashcat -m 29411 {header_path} --potfile-path {potfile_path}"
subprocess.Popen(cmd, shell=True)
```

## Rule: Validate All Paths Before Use

All paths passed as arguments must be validated as workspace-local:

```python
from portable_crypt_recovery.core.paths import safe_join_workspace

abs_path = safe_join_workspace(workspace_root, relative_path)
```

This raises `ValueError` if the resolved path escapes the workspace.

## Rule: No Original Volume Paths as Hashcat Input

Hashcat must never receive the original volume file as input.
It must only receive workspace-local normalized 512-byte headers or
workspace-derived hash input files.

## Rule: Windows CREATE_NO_WINDOW

On Windows, use `creationflags=subprocess.CREATE_NO_WINDOW` to prevent
a console window from flashing when Hashcat runs.

## Rule: command_array is list[str]

The `command_array` field in `QueuedJob` stores the full Hashcat argument list.
It is always `list[str]`, never a single string. Storing it as a list allows
safe logging, review, and re-execution without shell parsing.
