"""Candidate ORF discovery using explicit, testable rules."""

from __future__ import annotations

from Bio.Data import CodonTable
from Bio.Seq import Seq

from biopilot.schemas.results import ToolResult
from biopilot.tools.validation import InputValidationError, validate_dna


def find_orfs(
    sequence: str,
    min_nt_length: int = 90,
    include_reverse: bool = True,
    genetic_code: int = 1,
) -> ToolResult:
    """Find start-to-first-in-frame-stop candidate ORFs on one or both strands.

    Coordinates are 0-based with an exclusive end, always expressed against the
    supplied forward-strand sequence. A candidate starts at an accepted table
    start codon and ends immediately after its first in-frame stop codon.
    """
    try:
        dna = validate_dna(sequence)
        if not isinstance(min_nt_length, int) or min_nt_length < 3:
            raise InputValidationError("min_nt_length must be an integer of at least 3.")
        table = CodonTable.unambiguous_dna_by_id[genetic_code]
    except (InputValidationError, KeyError) as exc:
        return ToolResult.failure("find_orfs", f"Invalid ORF parameters: {exc}")

    records: list[dict[str, object]] = []
    strands = [("+", dna)]
    if include_reverse:
        strands.append(("-", str(Seq(dna).reverse_complement())))
    for strand, oriented in strands:
        for frame in range(3):
            for start in range(frame, len(oriented) - 2, 3):
                codon = oriented[start : start + 3]
                if codon not in table.start_codons:
                    continue
                stop_end: int | None = None
                for pos in range(start + 3, len(oriented) - 2, 3):
                    if oriented[pos : pos + 3] in table.stop_codons:
                        stop_end = pos + 3
                        break
                if stop_end is None or stop_end - start < min_nt_length:
                    continue
                nucleotide = oriented[start:stop_end]
                peptide = str(Seq(nucleotide[:-3]).translate(table=genetic_code))
                if strand == "+":
                    forward_start, forward_end = start, stop_end
                    frame_label = f"+{frame + 1}"
                else:
                    forward_start, forward_end = len(dna) - stop_end, len(dna) - start
                    frame_label = f"-{frame + 1}"
                records.append(
                    {
                        "strand": strand,
                        "frame": frame,
                        "frame_label": frame_label,
                        "start_0_based": forward_start,
                        "end_0_based_exclusive": forward_end,
                        "nucleotide_length": len(nucleotide),
                        "start_codon": nucleotide[:3],
                        "stop_codon": nucleotide[-3:],
                        "nucleotide_sequence": nucleotide,
                        "peptide": peptide,
                        "peptide_length": len(peptide),
                    }
                )
    records.sort(key=lambda record: (int(record["start_0_based"]), str(record["strand"])))
    warning = "Candidate ORFs are computational predictions, not confirmed genes."
    return ToolResult(
        tool="find_orfs",
        data={
            "orfs": records,
            "count": len(records),
            "minimum_nt_length": min_nt_length,
            "genetic_code": genetic_code,
            "coordinate_convention": "0-based, forward-reference coordinates; end is exclusive",
            "definition": "accepted start codon through first in-frame stop codon, inclusive",
        },
        warnings=[warning] if records else ["No complete candidate ORFs met the specified definition and length threshold.", warning],
    )

