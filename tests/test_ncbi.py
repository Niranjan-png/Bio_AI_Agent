from biopilot.tools.ncbi import search_ncbi


def test_ncbi_requires_email_without_network(monkeypatch) -> None:
    monkeypatch.setattr("biopilot.tools.ncbi.get_settings", lambda: type("S", (), {"ncbi_email": None, "ncbi_api_key": None})())
    result = search_ncbi("BRCA1")
    assert not result.ok
    assert "NCBI_EMAIL" in result.errors[0]

