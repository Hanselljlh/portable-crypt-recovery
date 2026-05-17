"""HashcatSetup model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HashcatSetup:
    """Configuration and status for the Hashcat executable."""

    executable_path: str | None = None
    is_portable: bool = False
    version_string: str | None = None
    verified: bool = False
    verified_timestamp: str | None = None
    selected_device_ids: list[int] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "executable_path": self.executable_path,
            "is_portable": self.is_portable,
            "version_string": self.version_string,
            "verified": self.verified,
            "verified_timestamp": self.verified_timestamp,
            "selected_device_ids": self.selected_device_ids,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HashcatSetup":
        return cls(
            executable_path=data.get("executable_path"),
            is_portable=data.get("is_portable", False),
            version_string=data.get("version_string"),
            verified=data.get("verified", False),
            verified_timestamp=data.get("verified_timestamp"),
            selected_device_ids=data.get("selected_device_ids", []),
        )
