"""Pairwise alignment with transparent identity and gap calculations."""

from __future__ import annotations

from Bio.Align import PairwiseAligner

from biopilot.schemas.results import ToolResult
from biopilot.tools.validation import InputValidationError, validate_dna


def align_sequences(
    sequence_a: str,
    sequence_b: str,
    mode: str = "global",
    match_score: float = 2.0,
    mismatch_score: float = -1.0,
    gap_open_score: float = -2.0,
    gap_extend_score: float = -0.5,
) -> ToolResult:
    """Perform global or local DNA alignment and report an explicit identity basis."""
    try:
        a, b = validate_dna(sequence_a), validate_dna(sequence_b)
        if mode not in {"global", "local"}:
            raise InputValidationError("Alignment mode must be 'global' or 'local'.")
        values = (match_score, mismatch_score, gap_open_score, gap_extend_score)
        if not all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values):
            raise InputValidationError("Alignment scores must be numeric.")
    except InputValidationError as exc:
        return ToolResult.failure("align_sequences", str(exc))
    aligner = PairwiseAligner(mode=mode)
    aligner.match_score = match_score
    aligner.mismatch_score = mismatch_score
    aligner.open_gap_score = gap_open_score
    aligner.extend_gap_score = gap_extend_score
    try:
        alignment = aligner.align(a, b)[0]
    except Exception as exc:  # BioPython may reject unusual scoring combinations.
        return ToolResult.failure("align_sequences", f"Alignment failed: {exc}")
    aligned_a, aligned_b = _render_alignment(alignment, a, b)
    matches = mismatches = insertions = deletions = 0
    for left, right in zip(aligned_a, aligned_b):
        if left == "-":
            insertions += 1
        elif right == "-":
            deletions += 1
        elif left == right and left in "ACGT":
            matches += 1
        else:
            mismatches += 1
    denominator = matches + mismatches + insertions + deletions
    return ToolResult(
        tool="align_sequences",
        data={
            "mode": mode,
            "score": float(alignment.score),
            "aligned_sequence_a": aligned_a,
            "aligned_sequence_b": aligned_b,
            "alignment_text": str(alignment),
            "matches": matches,
            "mismatches": mismatches,
            "insertions_relative_to_a": insertions,
            "deletions_relative_to_a": deletions,
            "percent_identity": round(matches / denominator * 100, 4) if denominator else 0.0,
            "identity_denominator": "aligned columns, including mismatch and gap columns; ambiguous symbols do not count as matches",
            "parameters": {"match": match_score, "mismatch": mismatch_score, "gap_open": gap_open_score, "gap_extend": gap_extend_score},
        },
        warnings=["Alignment score is not percent identity and does not independently establish evolutionary or medical significance."],
        provenance={"library": "BioPython PairwiseAligner"},
    )


def _render_alignment(alignment: object, sequence_a: str, sequence_b: str) -> tuple[str, str]:
    """Render BioPython coordinate blocks as equal-length gapped strings."""
    coordinates = alignment.coordinates  # type: ignore[attr-defined]
    a_parts: list[str] = []
    b_parts: list[str] = []
    for index in range(coordinates.shape[1] - 1):
        a_start, a_end = int(coordinates[0, index]), int(coordinates[0, index + 1])
        b_start, b_end = int(coordinates[1, index]), int(coordinates[1, index + 1])
        a_segment, b_segment = sequence_a[a_start:a_end], sequence_b[b_start:b_end]
        if a_end == a_start:
            a_segment = "-" * len(b_segment)
        elif b_end == b_start:
            b_segment = "-" * len(a_segment)
        a_parts.append(a_segment)
        b_parts.append(b_segment)
    return "".join(a_parts), "".join(b_parts)

