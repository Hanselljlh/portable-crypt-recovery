"""PimSet model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PimSet:
    """A set of PIM values for Hashcat jobs."""

    pim_set_id: str
    nickname: str = ""
    pim_mode: str = "default"  # "default" | "custom"
    values: list[int] = field(default_factory=list)  # sorted ascending
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "pim_set_id": self.pim_set_id,
            "nickname": self.nickname,
            "pim_mode": self.pim_mode,
            "values": self.values,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PimSet:
        return cls(
            pim_set_id=data["pim_set_id"],
            nickname=data.get("nickname", ""),
            pim_mode=data.get("pim_mode", "default"),
            values=data.get("values", []),
            notes=data.get("notes", ""),
        )
