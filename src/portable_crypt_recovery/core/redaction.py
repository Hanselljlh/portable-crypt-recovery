"""Simple redaction helpers for logs and diagnostic bundles."""

from __future__ import annotations

SENSITIVE_KEYS = {
    "password",
    "password_found",
    "potfile",
    "header",
    "keyfile",
    "cracked_result",
}


def redact_dict(data: dict) -> dict:
    """Return a shallow redacted copy of a dictionary."""
    output = {}
    for key, value in data.items():
        if any(token in key.lower() for token in SENSITIVE_KEYS):
            output[key] = "<redacted>"
        else:
            output[key] = value
    return output
