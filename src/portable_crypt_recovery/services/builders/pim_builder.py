"""PIM parsing and expansion."""

from __future__ import annotations

import re
from pathlib import Path

from portable_crypt_recovery.core.ids import new_id
from portable_crypt_recovery.models.pim_set import PimSet

_SPLIT_RE = re.compile(r"[,\n]+")
_RANGE_RE = re.compile(r"^(\d+)\s*-\s*(\d+)$")

# Limits
_WARN_ABOVE = 100
_REQUIRE_CONFIRM_ABOVE = 1000
_BLOCK_ABOVE = 10000


class PimLimitWarning(UserWarning):
    """Raised when PIM count exceeds warning threshold."""


class PimLimitConfirmRequired(Exception):
    """Raised when PIM count requires confirmation."""


class PimLimitBlocked(Exception):
    """Raised when PIM count exceeds the hard block limit."""


def expand_pim_input(raw_input: str) -> list[int]:
    """Expand comma/newline separated PIM values and ranges."""
    values: list[int] = []
    for part in _SPLIT_RE.split(raw_input):
        token = part.strip()
        if not token:
            continue
        range_match = _RANGE_RE.match(token)
        if range_match:
            start = int(range_match.group(1))
            stop = int(range_match.group(2))
            if start <= 0 or stop <= 0:
                raise ValueError("PIM ranges must use positive integers.")
            if start > stop:
                raise ValueError(f"Invalid range: {token}")
            values.extend(range(start, stop + 1))
            continue
        if not token.isdigit():
            raise ValueError(f"Invalid PIM value: {token}")
        value = int(token)
        if value <= 0:
            raise ValueError("Use default PIM mode instead of entering 0.")
        values.append(value)
    if not values:
        raise ValueError("PIM list is empty.")
    return sorted(set(values))


def build_pim_set(
    raw_input: str,
    workspace_root: Path | None = None,
    force: bool = False,
) -> PimSet:
    """Parse raw PIM input, validate, and return a PimSet.

    Parameters
    ----------
    raw_input:
        Comma or newline separated integers and ranges.
    workspace_root:
        If provided, save the PIM list to generated/pim-lists/.
    force:
        If True, bypass the confirm/block limits.
    """
    import warnings

    values = expand_pim_input(raw_input)
    count = len(values)

    if not force:
        if count > _BLOCK_ABOVE:
            raise PimLimitBlocked(
                f"PIM list has {count} values, which exceeds the limit of {_BLOCK_ABOVE}. "
                "Use force=True to override."
            )
        if count > _REQUIRE_CONFIRM_ABOVE:
            raise PimLimitConfirmRequired(
                f"PIM list has {count} values. Confirm before continuing."
            )
        if count > _WARN_ABOVE:
            warnings.warn(
                f"PIM list has {count} values (above {_WARN_ABOVE}).",
                PimLimitWarning,
                stacklevel=2,
            )

    pim_set = PimSet(
        pim_set_id=new_id("pimset"),
        pim_mode="custom",
        values=values,
    )

    if workspace_root is not None:
        _save_pim_list(workspace_root, pim_set)

    return pim_set


def build_default_pim_set() -> PimSet:
    """Return a PimSet representing the default PIM (no custom value)."""
    return PimSet(
        pim_set_id=new_id("pimset"),
        pim_mode="default",
        values=[],
    )


def _save_pim_list(workspace_root: Path, pim_set: PimSet) -> None:
    from portable_crypt_recovery.core.atomic_write import atomic_write_json

    out_dir = workspace_root / "generated" / "pim-lists"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{pim_set.pim_set_id}.json"
    atomic_write_json(out_path, pim_set.to_dict())
