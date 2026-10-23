from biopilot.tools.sequence_analysis import analyze_dna, translate_dna


def test_dna_statistics_normalizes_lowercase_and_reports_literal_gc() -> None:
    result = analyze_dna("acgtn")
    assert result.ok
    assert result.data["length"] == 5
    assert result.data["counts"] == {"A": 1, "C": 1, "G": 1, "T": 1, "N": 1}
    assert result.data["gc_percent"] == 40.0
    assert result.data["reverse_complement"] == "NACGT"


def test_dna_statistics_rejects_empty_and_invalid_symbols() -> None:
    assert not analyze_dna("   ").ok
    result = analyze_dna("ATGZ")
    assert not result.ok and "Z" in result.errors[0]


def test_translation_known_codon_stop_and_incomplete_handling() -> None:
    result = translate_dna("ATGTAA", frame=0)
    assert result.ok and result.data["peptide"] == "M*"
    assert result.data["stop_positions_1_based"] == [2]
    assert not translate_dna("ATGA", frame=0).ok
    trimmed = translate_dna("ATGA", frame=0, trim_incomplete_codon=True)
    assert trimmed.ok and trimmed.data["peptide"] == "M"


def test_translation_frame_validation() -> None:
    assert translate_dna("AATGAA", frame=1, trim_incomplete_codon=True).data["peptide"] == "M"
    assert not translate_dna("ATGAAA", frame=3).ok

