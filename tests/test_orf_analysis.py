from biopilot.tools.orf_analysis import find_orfs


def test_forward_orf_coordinates_are_zero_based_end_exclusive() -> None:
    result = find_orfs("CCCATGAAATAACCC", min_nt_length=9, include_reverse=False)
    assert result.ok and result.data["count"] == 1
    orf = result.data["orfs"][0]
    assert (orf["start_0_based"], orf["end_0_based_exclusive"], orf["peptide"]) == (3, 12, "MK")


def test_reverse_orf_and_filters() -> None:
    result = find_orfs("TTATTTCAT", min_nt_length=9)
    assert result.data["count"] == 1
    assert result.data["orfs"][0]["strand"] == "-"
    assert find_orfs("ATGAAATAA", min_nt_length=12).data["count"] == 0


def test_no_complete_orf_is_valid_empty_result() -> None:
    result = find_orfs("CCCCCCCCCC", min_nt_length=3)
    assert result.ok and result.data["orfs"] == []

