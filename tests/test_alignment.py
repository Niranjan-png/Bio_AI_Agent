from biopilot.tools.alignment import align_sequences


def test_identical_global_alignment_has_full_identity() -> None:
    result = align_sequences("ACGT", "ACGT")
    assert result.ok and result.data["percent_identity"] == 100.0
    assert result.data["matches"] == 4


def test_substitution_and_indel_are_summarized() -> None:
    substitution = align_sequences("ACGT", "AGGT")
    assert substitution.data["mismatches"] == 1
    indel = align_sequences("ACGT", "ACGGT")
    assert indel.ok and indel.data["insertions_relative_to_a"] == 1


def test_local_alignment_and_invalid_inputs() -> None:
    assert align_sequences("TTACGTAA", "GGACGTCC", mode="local").ok
    assert not align_sequences("", "ACGT").ok
    assert not align_sequences("ACGT", "ACGT", mode="bad").ok

