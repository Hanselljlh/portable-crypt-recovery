"""Parse cracked PIM value and password from Hashcat outfile/potfile lines.

When Hashcat cracks a VeraCrypt/TrueCrypt hash with a PIM range
(--veracrypt-pim-start N --veracrypt-pim-stop M), the potfile/outfile
embeds the matched PIM:
    $veracrypt$1$<salt_hex>$<enc_hex>$PIM=<value>:<password>

Single-PIM jobs produce no PIM annotation in the output.
"""

from __future__ import annotations

import re

# Matches both "$PIM=485" (hashcat outfile) and ":PIM=485" (alternative format)
_PIM_RE = re.compile(r"\$PIM=(\d+)|:PIM=(\d+)", re.IGNORECASE)


def extract_cracked_pim(line: str) -> int | None:
    """Return the PIM value embedded in a Hashcat cracked output line.

    Returns None when the line contains no PIM annotation (single-PIM jobs).
    """
    m = _PIM_RE.search(line)
    if not m:
        return None
    raw = m.group(1) or m.group(2)
    return int(raw)


def extract_password_from_line(line: str) -> str:
    """Extract the password from a cracked output line.

    Handles both:
      hash:password                           (single-PIM job)
      hash$PIM=<value>:password               (PIM range job, $PIM= format)
      hash:PIM=<value>:password               (PIM range job, :PIM= format)

    Returns everything after the PIM section if present, otherwise everything
    after the first colon.
    """
    m = _PIM_RE.search(line)
    if m:
        after = line[m.end():]
        # After $PIM=485 comes ":password"; after :PIM=485 also comes ":password"
        if after.startswith(":"):
            return after[1:]
        return after
    # Standard format: everything after first ":"
    if ":" in line:
        return line.split(":", 1)[1]
    return line
