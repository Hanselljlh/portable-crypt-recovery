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
    # Performance flags passed to hashcat at run time
    use_optimized_kernels: bool = True   # -O  (2-4× faster; max ~31-char passwords)
    use_cpu_opencl: bool = False         # -D 1 (CPU OpenCL; 3-5× faster if runtime installed)
    ignore_cuda: bool = False            # --backend-ignore-cuda (skip CUDA; CPU fallback)
    batch_adjacent_pims: bool = False  # opt-in: group adjacent PIMs into ranges

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "executable_path": self.executable_path,
            "is_portable": self.is_portable,
            "version_string": self.version_string,
            "verified": self.verified,
            "verified_timestamp": self.verified_timestamp,
            "selected_device_ids": self.selected_device_ids,
            "use_optimized_kernels": self.use_optimized_kernels,
            "use_cpu_opencl": self.use_cpu_opencl,
            "ignore_cuda": self.ignore_cuda,
            "batch_adjacent_pims": self.batch_adjacent_pims,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HashcatSetup:
        return cls(
            executable_path=data.get("executable_path"),
            is_portable=data.get("is_portable", False),
            version_string=data.get("version_string"),
            verified=data.get("verified", False),
            verified_timestamp=data.get("verified_timestamp"),
            selected_device_ids=data.get("selected_device_ids") or [],
            use_optimized_kernels=data.get("use_optimized_kernels", True),
            use_cpu_opencl=data.get("use_cpu_opencl", False),
            ignore_cuda=data.get("ignore_cuda", False),
            batch_adjacent_pims=data.get("batch_adjacent_pims", False),
        )
