from biopilot.workflows.analysis_workflow import run_analysis


def test_comprehensive_workflow_runs_expected_tools_and_report(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("biopilot.tools.reporting.get_settings", lambda: type("S", (), {"reports_dir": tmp_path})())
    outcome = run_analysis("ATGAAATAA", "comprehensive", "ATGAAA", min_orf_length=9, create_report=True)
    assert {"statistics", "translation", "orf", "alignment", "report"} <= outcome["results"].keys()
    assert outcome["results"]["alignment"]["ok"]
    assert outcome["results"]["report"]["data"]["html"].endswith(".html")


def test_invalid_input_stops_dependent_workflow_steps() -> None:
    outcome = run_analysis("ATG!", "comprehensive")
    assert not outcome["results"]["statistics"]["ok"]
    assert len(outcome["execution"]) == 1

