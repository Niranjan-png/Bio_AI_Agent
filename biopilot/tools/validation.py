"""Untrusted-input validation shared by local analysis tools."""

from __future__ import annotations

import re

from biopilot.config import get_settings

DNA_IUPAC = frozenset("ACGTRYSWKMBDHVN")
PROTEIN_IUPAC = frozenset("ACDEFGHIKLMNPQRSTVWYBXZJUO*-")


class InputValidationError(ValueError):
    """Raised when user-provided data cannot safely enter an analysis."""


def normalize_sequence(sequence: str, *, allow_gap: bool = False) -> str:
    """Remove whitespace, uppercase sequence text, and enforce size limit."""
    if not isinstance(sequence, str):
        raise InputValidationError("Sequence must be text.")
    normalized = re.sub(r"\s+", "", sequence).upper()
    if not normalized:
        raise InputValidationError("Sequence is empty after whitespace is removed.")
    if len(normalized) > get_settings().max_sequence_length:
        raise InputValidationError("Sequence exceeds the configured length limit.")
    if not allow_gap and "-" in normalized:
        raise InputValidationError("Gaps ('-') are not allowed in raw sequence input.")
    return normalized


def validate_dna(sequence: str, *, allow_gap: bool = False) -> str:
    """Normalize an IUPAC DNA sequence and reject unsupported symbols."""
    normalized = normalize_sequence(sequence, allow_gap=allow_gap)
    allowed = DNA_IUPAC | ({"-"} if allow_gap else set())
    invalid = sorted(set(normalized) - allowed)
    if invalid:
        raise InputValidationError(
            "Invalid DNA symbol(s): " + ", ".join(repr(symbol) for symbol in invalid)
        )
    return normalized


def validate_frame(frame: int) -> int:
    """Validate a zero-based forward reading-frame offset."""
    if isinstance(frame, bool) or not isinstance(frame, int) or frame not in (0, 1, 2):
        raise InputValidationError("Reading frame must be integer 0, 1, or 2.")
    return frame

