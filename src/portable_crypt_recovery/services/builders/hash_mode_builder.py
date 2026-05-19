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

# ---------------------------------------------------------------------------
# Mode ordering philosophy
# ---------------------------------------------------------------------------
# Within each list, modes are ordered:
#   1. XTS key size ascending: 512-bit → 1024-bit → 1536-bit
#      (512-bit = single cipher, most common; cascades are rare)
#   2. KDF by real-world likelihood within each XTS tier
#
# For VeraCrypt non-system volumes the current default KDF is SHA-512;
# RIPEMD-160 was the older default.  System/boot volumes still default to
# RIPEMD-160.  For TrueCrypt, RIPEMD-160 has always been the default.
#
# This order ensures that the most likely combination cracks first and the
# queue runner (with stop-after-crack logic) can skip the remaining cascade
# modes once the volume is open.
# ---------------------------------------------------------------------------

# Cipher suffix strings reused across tables.
# XTS 512 = single cipher (AES, Serpent, or Twofish — mode covers all three)
# XTS 1024 = two-cipher cascade (AES-Twofish, Serpent-AES, or Twofish-Serpent)
# XTS 1536 = three-cipher cascade (AES-Twofish-Serpent only)
_C1 = "AES / Serpent / Twofish"
_C2 = "AES-Twofish / Serpent-AES / Twofish-Serpent"
_C3 = "AES-Twofish-Serpent"

# Current TrueCrypt non-system modes  (RIPEMD-160 is TC default)
_TC_CURRENT_NONSYSTEM: list[tuple[int, str]] = [
    # XTS 512 bit — single cipher, most common
    (29311, f"TrueCrypt RIPEMD160 | XTS 512 bit — {_C1}"),
    (29321, f"TrueCrypt SHA512 | XTS 512 bit — {_C1}"),
    (29331, f"TrueCrypt Whirlpool | XTS 512 bit — {_C1}"),
    # XTS 1024 bit — two-cipher cascade
    (29312, f"TrueCrypt RIPEMD160 | XTS 1024 bit — {_C2}"),
    (29322, f"TrueCrypt SHA512 | XTS 1024 bit — {_C2}"),
    (29332, f"TrueCrypt Whirlpool | XTS 1024 bit — {_C2}"),
    # XTS 1536 bit — three-cipher cascade
    (29313, f"TrueCrypt RIPEMD160 | XTS 1536 bit — {_C3}"),
    (29323, f"TrueCrypt SHA512 | XTS 1536 bit — {_C3}"),
    (29333, f"TrueCrypt Whirlpool | XTS 1536 bit — {_C3}"),
]

# Current TrueCrypt system/boot modes  (only RIPEMD-160 supported)
_TC_CURRENT_SYSTEM: list[tuple[int, str]] = [
    (29341, f"TrueCrypt RIPEMD160 | XTS 512 bit — {_C1} [boot]"),
    (29342, f"TrueCrypt RIPEMD160 | XTS 1024 bit — {_C2} [boot]"),
    (29343, f"TrueCrypt RIPEMD160 | XTS 1536 bit — {_C3} [boot]"),
]

# Legacy TrueCrypt non-system modes
_TC_LEGACY_NONSYSTEM: list[tuple[int, str]] = [
    # XTS 512 bit
    (6211, f"TrueCrypt PBKDF2-HMAC-RIPEMD160 | XTS 512 bit — {_C1}"),
    (6221, f"TrueCrypt PBKDF2-HMAC-SHA512 | XTS 512 bit — {_C1}"),
    (6231, f"TrueCrypt PBKDF2-HMAC-Whirlpool | XTS 512 bit — {_C1}"),
    # XTS 1024 bit
    (6212, f"TrueCrypt PBKDF2-HMAC-RIPEMD160 | XTS 1024 bit — {_C2}"),
    (6222, f"TrueCrypt PBKDF2-HMAC-SHA512 | XTS 1024 bit — {_C2}"),
    (6232, f"TrueCrypt PBKDF2-HMAC-Whirlpool | XTS 1024 bit — {_C2}"),
    # XTS 1536 bit
    (6213, f"TrueCrypt PBKDF2-HMAC-RIPEMD160 | XTS 1536 bit — {_C3}"),
    (6223, f"TrueCrypt PBKDF2-HMAC-SHA512 | XTS 1536 bit — {_C3}"),
    (6233, f"TrueCrypt PBKDF2-HMAC-Whirlpool | XTS 1536 bit — {_C3}"),
]

# Legacy TrueCrypt system/boot modes
_TC_LEGACY_SYSTEM: list[tuple[int, str]] = [
    (6241, f"TrueCrypt PBKDF2-HMAC-RIPEMD160 | XTS 512 bit — {_C1} [boot]"),
    (6242, f"TrueCrypt PBKDF2-HMAC-RIPEMD160 | XTS 1024 bit — {_C2} [boot]"),
    (6243, f"TrueCrypt PBKDF2-HMAC-RIPEMD160 | XTS 1536 bit — {_C3} [boot]"),
]

# Current VeraCrypt non-system modes  (SHA-512 is current VC default KDF)
_VC_CURRENT_NONSYSTEM: list[tuple[int, str]] = [
    # XTS 512 bit — single cipher, most common
    (29421, f"VeraCrypt SHA512 | XTS 512 bit — {_C1}"),       # current VeraCrypt default
    (29411, f"VeraCrypt RIPEMD160 | XTS 512 bit — {_C1}"),    # older VeraCrypt default
    (29451, f"VeraCrypt SHA256 | XTS 512 bit — {_C1}"),
    (29431, f"VeraCrypt Whirlpool | XTS 512 bit — {_C1}"),
    (29471, f"VeraCrypt Streebog-512 | XTS 512 bit — {_C1}"),
    # XTS 1024 bit — two-cipher cascade
    (29422, f"VeraCrypt SHA512 | XTS 1024 bit — {_C2}"),
    (29412, f"VeraCrypt RIPEMD160 | XTS 1024 bit — {_C2}"),
    (29452, f"VeraCrypt SHA256 | XTS 1024 bit — {_C2}"),
    (29432, f"VeraCrypt Whirlpool | XTS 1024 bit — {_C2}"),
    (29472, f"VeraCrypt Streebog-512 | XTS 1024 bit — {_C2}"),
    # XTS 1536 bit — three-cipher cascade
    (29423, f"VeraCrypt SHA512 | XTS 1536 bit — {_C3}"),
    (29413, f"VeraCrypt RIPEMD160 | XTS 1536 bit — {_C3}"),
    (29453, f"VeraCrypt SHA256 | XTS 1536 bit — {_C3}"),
    (29433, f"VeraCrypt Whirlpool | XTS 1536 bit — {_C3}"),
    (29473, f"VeraCrypt Streebog-512 | XTS 1536 bit — {_C3}"),
]

# Current VeraCrypt system/boot modes  (RIPEMD-160 is still boot default)
_VC_CURRENT_SYSTEM: list[tuple[int, str]] = [
    # XTS 512 bit
    (29441, f"VeraCrypt RIPEMD160 | XTS 512 bit — {_C1} [boot]"),   # boot default
    (29461, f"VeraCrypt SHA256 | XTS 512 bit — {_C1} [boot]"),
    (29481, f"VeraCrypt Streebog-512 | XTS 512 bit — {_C1} [boot]"),
    # XTS 1024 bit
    (29442, f"VeraCrypt RIPEMD160 | XTS 1024 bit — {_C2} [boot]"),
    (29462, f"VeraCrypt SHA256 | XTS 1024 bit — {_C2} [boot]"),
    (29482, f"VeraCrypt Streebog-512 | XTS 1024 bit — {_C2} [boot]"),
    # XTS 1536 bit
    (29443, f"VeraCrypt RIPEMD160 | XTS 1536 bit — {_C3} [boot]"),
    (29463, f"VeraCrypt SHA256 | XTS 1536 bit — {_C3} [boot]"),
    (29483, f"VeraCrypt Streebog-512 | XTS 1536 bit — {_C3} [boot]"),
]

# Legacy VeraCrypt non-system modes
_VC_LEGACY_NONSYSTEM: list[tuple[int, str]] = [
    # XTS 512 bit — single cipher, most common
    (13721, f"VeraCrypt PBKDF2-HMAC-SHA512 | XTS 512 bit — {_C1}"),       # current VC default
    (13711, f"VeraCrypt PBKDF2-HMAC-RIPEMD160 | XTS 512 bit — {_C1}"),    # older VC default
    (13751, f"VeraCrypt PBKDF2-HMAC-SHA256 | XTS 512 bit — {_C1}"),
    (13731, f"VeraCrypt PBKDF2-HMAC-Whirlpool | XTS 512 bit — {_C1}"),
    (13771, f"VeraCrypt PBKDF2-HMAC-Streebog-512 | XTS 512 bit — {_C1}"),
    # XTS 1024 bit — two-cipher cascade
    (13722, f"VeraCrypt PBKDF2-HMAC-SHA512 | XTS 1024 bit — {_C2}"),
    (13712, f"VeraCrypt PBKDF2-HMAC-RIPEMD160 | XTS 1024 bit — {_C2}"),
    (13752, f"VeraCrypt PBKDF2-HMAC-SHA256 | XTS 1024 bit — {_C2}"),
    (13732, f"VeraCrypt PBKDF2-HMAC-Whirlpool | XTS 1024 bit — {_C2}"),
    (13772, f"VeraCrypt PBKDF2-HMAC-Streebog-512 | XTS 1024 bit — {_C2}"),
    # XTS 1536 bit — three-cipher cascade
    (13723, f"VeraCrypt PBKDF2-HMAC-SHA512 | XTS 1536 bit — {_C3}"),
    (13713, f"VeraCrypt PBKDF2-HMAC-RIPEMD160 | XTS 1536 bit — {_C3}"),
    (13753, f"VeraCrypt PBKDF2-HMAC-SHA256 | XTS 1536 bit — {_C3}"),
    (13733, f"VeraCrypt PBKDF2-HMAC-Whirlpool | XTS 1536 bit — {_C3}"),
    (13773, f"VeraCrypt PBKDF2-HMAC-Streebog-512 | XTS 1536 bit — {_C3}"),
]

# Legacy VeraCrypt system/boot modes
_VC_LEGACY_SYSTEM: list[tuple[int, str]] = [
    # XTS 512 bit
    (13741, f"VeraCrypt PBKDF2-HMAC-RIPEMD160 | XTS 512 bit — {_C1} [boot]"),  # boot default
    (13761, f"VeraCrypt PBKDF2-HMAC-SHA256 | XTS 512 bit — {_C1} [boot]"),
    (13781, f"VeraCrypt PBKDF2-HMAC-Streebog-512 | XTS 512 bit — {_C1} [boot]"),
    # XTS 1024 bit
    (13742, f"VeraCrypt PBKDF2-HMAC-RIPEMD160 | XTS 1024 bit — {_C2} [boot]"),
    (13762, f"VeraCrypt PBKDF2-HMAC-SHA256 | XTS 1024 bit — {_C2} [boot]"),
    (13782, f"VeraCrypt PBKDF2-HMAC-Streebog-512 | XTS 1024 bit — {_C2} [boot]"),
    # XTS 1536 bit
    (13743, f"VeraCrypt PBKDF2-HMAC-RIPEMD160 | XTS 1536 bit — {_C3} [boot]"),
    (13763, f"VeraCrypt PBKDF2-HMAC-SHA256 | XTS 1536 bit — {_C3} [boot]"),
    (13783, f"VeraCrypt PBKDF2-HMAC-Streebog-512 | XTS 1536 bit — {_C3} [boot]"),
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


def _cipher_cascade_from_mode(mode: int) -> int:
    """Derive cipher cascade level from mode number last digit (1/2/3)."""
    last = mode % 10
    if last in (1, 2, 3):
        return last
    return 0


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
            cipher_cascade=_cipher_cascade_from_mode(m),
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
                    cipher_cascade=_cipher_cascade_from_mode(mode_num),
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
                        cipher_cascade=_cipher_cascade_from_mode(mode_num),
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


# ---------------------------------------------------------------------------
# KDF and XTS hint filtering
# ---------------------------------------------------------------------------

# Maps the user-facing KDF identifier to a substring that appears in every
# matching entry label in the mode tables above.
KDF_LABEL_MAP: dict[str, str] = {
    "sha512": "SHA512",
    "ripemd160": "RIPEMD160",
    "sha256": "SHA256",
    "whirlpool": "Whirlpool",
    "streebog512": "Streebog",
}

# Maps XTS key-size (int, bits) to the substring that appears in labels.
XTS_LABEL_MAP: dict[int, str] = {
    512: "XTS 512",
    1024: "XTS 1024",
    1536: "XTS 1536",
}

# KDFs that are not valid for TrueCrypt (used by wizard constraint wiring).
TRUECRYPT_UNSUPPORTED_KDFS: frozenset[str] = frozenset({"sha256", "streebog512"})


def filter_by_hints(
    mode_set: HashModeSet,
    known_kdfs: list[str],
    known_xts_sizes: list[int],
) -> None:
    """Filter *mode_set.entries* in-place by KDF and XTS hints.

    Empty lists mean "no filter" — all entries pass.
    """
    if known_kdfs:
        keep = {KDF_LABEL_MAP[k] for k in known_kdfs if k in KDF_LABEL_MAP}
        if keep:
            mode_set.entries = [
                e for e in mode_set.entries if any(kw in e.label for kw in keep)
            ]
    if known_xts_sizes:
        keep = {XTS_LABEL_MAP[s] for s in known_xts_sizes if s in XTS_LABEL_MAP}
        if keep:
            mode_set.entries = [
                e for e in mode_set.entries if any(kw in e.label for kw in keep)
            ]


def veracrypt_only_modes() -> frozenset[int]:
    """Return mode numbers that are only valid for VeraCrypt (not TrueCrypt)."""
    return _VC_ONLY_MODES


def truecrypt_only_modes() -> frozenset[int]:
    """Return mode numbers that are only valid for TrueCrypt."""
    return _TC_ONLY_MODES


def system_modes() -> frozenset[int]:
    """Return mode numbers that are system/boot modes."""
    return _SYSTEM_MODES
