"""BioPython-backed DNA statistics and translation tools."""

from __future__ import annotations

from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction

from biopilot.schemas.results import ToolResult
from biopilot.tools.validation import DNA_IUPAC, InputValidationError, validate_dna, validate_frame


def analyze_dna(sequence: str, sequence_id: str = "query") -> ToolResult:
    """Calculate reproducible DNA composition and GC statistics.

    GC percentage uses the count of literal G/C bases divided by full sequence
    length, so ambiguous bases (including N) remain in the explicit denominator.
    """
    try:
        dna = validate_dna(sequence)
    except InputValidationError as exc:
        return ToolResult.failure("analyze_dna", str(exc))
    counts = {base: dna.count(base) for base in "ACGTN"}
    ambiguous = {base: dna.count(base) for base in sorted(DNA_IUPAC - set("ACGTN")) if dna.count(base)}
    gc_percent = round((counts["G"] + counts["C"]) / len(dna) * 100, 4)
    warnings = []
    if ambiguous:
        warnings.append("IUPAC ambiguity symbols are retained but do not contribute to literal G/C counts.")
    if counts["N"]:
        warnings.append("N bases are included in the GC denominator and indicate unknown nucleotide identity.")
    return ToolResult(
        tool="analyze_dna",
        data={
            "sequence_id": sequence_id,
            "length": len(dna),
            "counts": counts,
            "ambiguous_counts": ambiguous,
            "gc_percent": gc_percent,
            "gc_denominator": "all sequence characters, including IUPAC ambiguity symbols",
            "biopython_gc_fraction": round(gc_fraction(dna, ambiguous="ignore") * 100, 4),
            "reverse_complement": str(Seq(dna).reverse_complement()),
            "alphabet": "IUPAC DNA",
        },
        warnings=warnings,
        provenance={"library": "BioPython", "calculation": "literal G+C / total length * 100"},
    )


def translate_dna(
    sequence: str,
    frame: int = 0,
    genetic_code: int = 1,
    trim_incomplete_codon: bool = False,
    require_start: bool = False,
) -> ToolResult:
    """Translate a selected reading frame with explicit terminal-codon handling."""
    try:
        dna = validate_dna(sequence)
        frame = validate_frame(frame)
        if not isinstance(genetic_code, int) or genetic_code < 1:
            raise InputValidationError("Genetic code must be a positive NCBI translation-table integer.")
    except InputValidationError as exc:
        return ToolResult.failure("translate_dna", str(exc))
    coding = dna[frame:]
    remainder = len(coding) % 3
    if remainder and not trim_incomplete_codon:
        return ToolResult.failure(
            "translate_dna",
            f"Selected frame has {remainder} trailing base(s); set trim_incomplete_codon=True to translate complete codons only.",
        )
    translated_input = coding[:-remainder] if remainder else coding
    if not translated_input:
        return ToolResult.failure("translate_dna", "No complete codon exists in the selected reading frame.")
    try:
        peptide = str(Seq(translated_input).translate(table=genetic_code, to_stop=False))
    except (ValueError, KeyError) as exc:
        return ToolResult.failure("translate_dna", f"Translation failed: {exc}")
    warnings: list[str] = [f"Translation uses NCBI genetic code table {genetic_code}."]
    if remainder:
        warnings.append(f"Ignored {remainder} trailing nucleotide(s), not a complete codon.")
    if require_start and not translated_input.startswith("ATG"):
        warnings.append("Selected frame does not start with ATG; translation is not asserted to begin at a start codon.")
    if "X" in peptide:
        warnings.append("X residues indicate ambiguous or untranslatable codons.")
    return ToolResult(
        tool="translate_dna",
        data={
            "frame": frame,
            "frame_label": f"+{frame + 1}",
            "genetic_code": genetic_code,
            "input_nucleotides": translated_input,
            "peptide": peptide,
            "peptide_length": len(peptide),
            "stop_positions_1_based": [i + 1 for i, residue in enumerate(peptide) if residue == "*"],
            "ambiguous_residue_positions_1_based": [i + 1 for i, residue in enumerate(peptide) if residue == "X"],
        },
        warnings=warnings + ["Translation alone does not establish a functional protein."],
    )

