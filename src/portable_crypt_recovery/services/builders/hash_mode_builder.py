"""Hash mode builder — maps container family + header type to Hashcat mode numbers.

VeraCrypt current modes (preferred): 29411-29483
VeraCrypt legacy modes: 13711-13783
TrueCrypt current modes: 29311-29343
TrueCrypt legacy modes: 6211-6243
"""

from __future__ import annotations

from portable_crypt_recovery.core.ids import new_id
from portable_crypt_recovery.models.hash_mode_set import HashModeEntry, HashModeSet

# ---------------------------------------------------------------------------
# Built-in mode tables
# ---------------------------------------------------------------------------

# Current TrueCrypt non-system modes
_TC_CURRENT_NONSYSTEM: list[tuple[int, str]] = [
    (29311, "TrueCrypt RIPEMD160 + XTS 512 bit"),
    (29312, "TrueCrypt RIPEMD160 + XTS 1024 bit"),
    (29313, "TrueCrypt RIPEMD160 + XTS 1536 bit"),
    (29321, "TrueCrypt SHA512 + XTS 512 bit"),
    (29322, "TrueCrypt SHA512 + XTS 1024 bit"),
    (29323, "TrueCrypt SHA512 + XTS 1536 bit"),
    (29331, "TrueCrypt Whirlpool + XTS 512 bit"),
    (29332, "TrueCrypt Whirlpool + XTS 1024 bit"),
    (29333, "TrueCrypt Whirlpool + XTS 1536 bit"),
]

# Current TrueCrypt system/boot modes
_TC_CURRENT_SYSTEM: list[tuple[int, str]] = [
    (29341, "TrueCrypt RIPEMD160 + XTS 512 bit + boot-mode"),
    (29342, "TrueCrypt RIPEMD160 + XTS 1024 bit + boot-mode"),
    (29343, "TrueCrypt RIPEMD160 + XTS 1536 bit + boot-mode"),
]

# Legacy TrueCrypt non-system modes
_TC_LEGACY_NONSYSTEM: list[tuple[int, str]] = [
    (6211, "TrueCrypt PBKDF2-HMAC-RIPEMD160 + XTS 512-bit"),
    (6212, "TrueCrypt PBKDF2-HMAC-RIPEMD160 + XTS 1024-bit"),
    (6213, "TrueCrypt PBKDF2-HMAC-RIPEMD160 + XTS 1536-bit"),
    (6221, "TrueCrypt PBKDF2-HMAC-SHA512 + XTS 512-bit"),
    (6222, "TrueCrypt PBKDF2-HMAC-SHA512 + XTS 1024-bit"),
    (6223, "TrueCrypt PBKDF2-HMAC-SHA512 + XTS 1536-bit"),
    (6231, "TrueCrypt PBKDF2-HMAC-Whirlpool + XTS 512-bit"),
    (6232, "TrueCrypt PBKDF2-HMAC-Whirlpool + XTS 1024-bit"),
    (6233, "TrueCrypt PBKDF2-HMAC-Whirlpool + XTS 1536-bit"),
]

# Legacy TrueCrypt system/boot modes
_TC_LEGACY_SYSTEM: list[tuple[int, str]] = [
    (6241, "TrueCrypt PBKDF2-HMAC-RIPEMD160 + XTS 512-bit + boot-mode"),
    (6242, "TrueCrypt PBKDF2-HMAC-RIPEMD160 + XTS 1024-bit + boot-mode"),
    (6243, "TrueCrypt PBKDF2-HMAC-RIPEMD160 + XTS 1536-bit + boot-mode"),
]

# Current VeraCrypt non-system modes
_VC_CURRENT_NONSYSTEM: list[tuple[int, str]] = [
    (29411, "VeraCrypt RIPEMD160 + XTS 512 bit"),
    (29412, "VeraCrypt RIPEMD160 + XTS 1024 bit"),
    (29413, "VeraCrypt RIPEMD160 + XTS 1536 bit"),
    (29421, "VeraCrypt SHA512 + XTS 512 bit"),
    (29422, "VeraCrypt SHA512 + XTS 1024 bit"),
    (29423, "VeraCrypt SHA512 + XTS 1536 bit"),
    (29431, "VeraCrypt Whirlpool + XTS 512 bit"),
    (29432, "VeraCrypt Whirlpool + XTS 1024 bit"),
    (29433, "VeraCrypt Whirlpool + XTS 1536 bit"),
    (29451, "VeraCrypt SHA256 + XTS 512 bit"),
    (29452, "VeraCrypt SHA256 + XTS 1024 bit"),
    (29453, "VeraCrypt SHA256 + XTS 1536 bit"),
    (29471, "VeraCrypt Streebog-512 + XTS 512 bit"),
    (29472, "VeraCrypt Streebog-512 + XTS 1024 bit"),
    (29473, "VeraCrypt Streebog-512 + XTS 1536 bit"),
]

# Current VeraCrypt system/boot modes
_VC_CURRENT_SYSTEM: list[tuple[int, str]] = [
    (29441, "VeraCrypt RIPEMD160 + XTS 512 bit + boot-mode"),
    (29442, "VeraCrypt RIPEMD160 + XTS 1024 bit + boot-mode"),
    (29443, "VeraCrypt RIPEMD160 + XTS 1536 bit + boot-mode"),
    (29461, "VeraCrypt SHA256 + XTS 512 bit + boot-mode"),
    (29462, "VeraCrypt SHA256 + XTS 1024 bit + boot-mode"),
    (29463, "VeraCrypt SHA256 + XTS 1536 bit + boot-mode"),
    (29481, "VeraCrypt Streebog-512 + XTS 512 bit + boot-mode"),
    (29482, "VeraCrypt Streebog-512 + XTS 1024 bit + boot-mode"),
    (29483, "VeraCrypt Streebog-512 + XTS 1536 bit + boot-mode"),
]

# Legacy VeraCrypt non-system modes
_VC_LEGACY_NONSYSTEM: list[tuple[int, str]] = [
    (13711, "VeraCrypt PBKDF2-HMAC-RIPEMD160 + XTS 512-bit"),
    (13712, "VeraCrypt PBKDF2-HMAC-RIPEMD160 + XTS 1024-bit"),
    (13713, "VeraCrypt PBKDF2-HMAC-RIPEMD160 + XTS 1536-bit"),
    (13721, "VeraCrypt PBKDF2-HMAC-SHA512 + XTS 512-bit"),
    (13722, "VeraCrypt PBKDF2-HMAC-SHA512 + XTS 1024-bit"),
    (13723, "VeraCrypt PBKDF2-HMAC-SHA512 + XTS 1536-bit"),
    (13731, "VeraCrypt PBKDF2-HMAC-Whirlpool + XTS 512-bit"),
    (13732, "VeraCrypt PBKDF2-HMAC-Whirlpool + XTS 1024-bit"),
    (13733, "VeraCrypt PBKDF2-HMAC-Whirlpool + XTS 1536-bit"),
    (13751, "VeraCrypt PBKDF2-HMAC-SHA256 + XTS 512-bit"),
    (13752, "VeraCrypt PBKDF2-HMAC-SHA256 + XTS 1024-bit"),
    (13753, "VeraCrypt PBKDF2-HMAC-SHA256 + XTS 1536-bit"),
    (13771, "VeraCrypt PBKDF2-HMAC-Streebog-512 + XTS 512-bit"),
    (13772, "VeraCrypt PBKDF2-HMAC-Streebog-512 + XTS 1024-bit"),
    (13773, "VeraCrypt PBKDF2-HMAC-Streebog-512 + XTS 1536-bit"),
]

# Legacy VeraCrypt system/boot modes
_VC_LEGACY_SYSTEM: list[tuple[int, str]] = [
    (13741, "VeraCrypt PBKDF2-HMAC-RIPEMD160 + XTS 512-bit + boot-mode"),
    (13742, "VeraCrypt PBKDF2-HMAC-RIPEMD160 + XTS 1024-bit + boot-mode"),
    (13743, "VeraCrypt PBKDF2-HMAC-RIPEMD160 + XTS 1536-bit + boot-mode"),
    (13761, "VeraCrypt PBKDF2-HMAC-SHA256 + XTS 512-bit + boot-mode"),
    (13762, "VeraCrypt PBKDF2-HMAC-SHA256 + XTS 1024-bit + boot-mode"),
    (13763, "VeraCrypt PBKDF2-HMAC-SHA256 + XTS 1536-bit + boot-mode"),
    (13781, "VeraCrypt PBKDF2-HMAC-Streebog-512 + XTS 512-bit + boot-mode"),
    (13782, "VeraCrypt PBKDF2-HMAC-Streebog-512 + XTS 1024-bit + boot-mode"),
    (13783, "VeraCrypt PBKDF2-HMAC-Streebog-512 + XTS 1536-bit + boot-mode"),
]

# All VeraCrypt-only mode numbers (not valid for TrueCrypt)
_VC_ONLY_MODES: frozenset[int] = frozenset(
    m for m, _ in (
        _VC_CURRENT_NONSYSTEM + _VC_CURRENT_SYSTEM + _VC_LEGACY_NONSYSTEM + _VC_LEGACY_SYSTEM
    )
)

# All TrueCrypt-only mode numbers
_TC_ONLY_MODES: frozenset[int] = frozenset(
    m for m, _ in (
        _TC_CURRENT_NONSYSTEM + _TC_CURRENT_SYSTEM + _TC_LEGACY_NONSYSTEM + _TC_LEGACY_SYSTEM
    )
)

# System-mode numbers (boot-mode)
_SYSTEM_MODES: frozenset[int] = frozenset(
    m for m, _ in (
        _TC_CURRENT_SYSTEM + _TC_LEGACY_SYSTEM + _VC_CURRENT_SYSTEM + _VC_LEGACY_SYSTEM
    )
)


def _is_system_candidate(candidate_type: str) -> bool:
    return candidate_type in ("normal_system_header", "hidden_system_candidate")


def _to_entries(
    mode_pairs: list[tuple[int, str]],
    family: str,
    is_system: bool,
    is_legacy: bool,
    candidate_type: str,
) -> list[HashModeEntry]:
    return [
        HashModeEntry(
            mode=m,
            label=label,
            family=family,
            is_system=is_system,
            is_legacy=is_legacy,
            candidate_type=candidate_type,
        )
        for m, label in mode_pairs
    ]


def build_mode_set(
    family: str,
    candidate_type: str,
    target_id: str = "",
    header_id: str = "",
    supported_modes: dict[int, str] | None = None,
    include_legacy: bool = True,
) -> HashModeSet:
    """Build a HashModeSet for the given family and header candidate type.

    Parameters
    ----------
    family:
        "veracrypt" | "truecrypt" | "both" | "unknown"
    candidate_type:
        "normal_volume_header" | "hidden_volume_header" | "normal_system_header"
        | "hidden_system_candidate" | "unknown_imported_header"
    supported_modes:
        If provided (from mode_scan), only include modes present in this dict.
        If None, use the built-in table without filtering.
    include_legacy:
        Whether to include legacy mode numbers.
    """
    is_system = _is_system_candidate(candidate_type)
    entries: list[HashModeEntry] = []
    seen: set[int] = set()

    families = _resolve_families(family)

    for fam in families:
        if fam == "veracrypt":
            if is_system:
                current = _VC_CURRENT_SYSTEM
                legacy = _VC_LEGACY_SYSTEM
            else:
                current = _VC_CURRENT_NONSYSTEM
                legacy = _VC_LEGACY_NONSYSTEM
        else:  # truecrypt
            if is_system:
                current = _TC_CURRENT_SYSTEM
                legacy = _TC_LEGACY_SYSTEM
            else:
                current = _TC_CURRENT_NONSYSTEM
                legacy = _TC_LEGACY_NONSYSTEM

        for mode_num, label in current:
            if mode_num in seen:
                continue
            if supported_modes is not None and mode_num not in supported_modes:
                continue
            entries.append(
                HashModeEntry(
                    mode=mode_num,
                    label=label,
                    family=fam,
                    is_system=is_system,
                    is_legacy=False,
                    candidate_type=candidate_type,
                )
            )
            seen.add(mode_num)

        if include_legacy:
            for mode_num, label in legacy:
                if mode_num in seen:
                    continue
                if supported_modes is not None and mode_num not in supported_modes:
                    continue
                entries.append(
                    HashModeEntry(
                        mode=mode_num,
                        label=label,
                        family=fam,
                        is_system=is_system,
                        is_legacy=True,
                        candidate_type=candidate_type,
                    )
                )
                seen.add(mode_num)

    return HashModeSet(
        mode_set_id=new_id("modeset"),
        target_id=target_id,
        header_id=header_id,
        entries=entries,
    )


def _resolve_families(family: str) -> list[str]:
    """Expand 'both'/'unknown' to explicit family list."""
    if family in ("both", "unknown"):
        return ["veracrypt", "truecrypt"]
    if family in ("veracrypt", "truecrypt"):
        return [family]
    return ["veracrypt", "truecrypt"]


def try_all_valid(
    family: str,
    candidate_type: str,
    target_id: str = "",
    header_id: str = "",
    supported_modes: dict[int, str] | None = None,
) -> HashModeSet:
    """Return all valid modes for a given family + header combo.

    This is the 'Try Every Valid VeraCrypt / TrueCrypt Mode' option.
    """
    return build_mode_set(
        family=family,
        candidate_type=candidate_type,
        target_id=target_id,
        header_id=header_id,
        supported_modes=supported_modes,
        include_legacy=True,
    )


def veracrypt_only_modes() -> frozenset[int]:
    """Return mode numbers that are only valid for VeraCrypt (not TrueCrypt)."""
    return _VC_ONLY_MODES


def truecrypt_only_modes() -> frozenset[int]:
    """Return mode numbers that are only valid for TrueCrypt."""
    return _TC_ONLY_MODES


def system_modes() -> frozenset[int]:
    """Return mode numbers that are system/boot modes."""
    return _SYSTEM_MODES
