"""Report redaction utilities."""

from __future__ import annotations

import copy
from typing import Any

# Fields that contain sensitive data to mask by default
_SENSITIVE_FIELDS = frozenset(
    [
        "cracked_password",
        "password",
        "recovered_password",
    ]
)

_MASK = "***REDACTED***"


def redact_report(report_dict: dict[str, Any], redact_passwords: bool = True) -> dict[str, Any]:
    """Return a copy of report_dict with sensitive fields masked.

    Parameters
    ----------
    report_dict:
        Report data dictionary.
    redact_passwords:
        If True, mask password fields.
    """
    result = copy.deepcopy(report_dict)
    if redact_passwords:
        _redact_recursive(result)
    return result


def _redact_recursive(data: Any) -> None:
    if isinstance(data, dict):
        for key in list(data.keys()):
            if key in _SENSITIVE_FIELDS and data[key] is not None:
                data[key] = _MASK
            else:
                _redact_recursive(data[key])
    elif isinstance(data, list):
        for item in data:
            _redact_recursive(item)
