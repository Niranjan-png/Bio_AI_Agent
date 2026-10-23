"""Validated workflow layer; it never requires model credentials for local work."""

from __future__ import annotations

from typing import Any, Literal

from biopilot.schemas.results import ExecutionEvent
from biopilot.tools.alignment import align_sequences
from biopilot.tools.orf_analysis import find_orfs
from biopilot.tools.reporting import generate_report
from biopilot.tools.sequence_analysis import analyze_dna, translate_dna

AnalysisMode = Literal["statistics", "translation", "orf", "alignment", "comprehensive"]


def run_analysis(
    primary_sequence: str,
    mode: AnalysisMode = "comprehensive",
    comparison_sequence: str | None = None,
    *,
    frame: int = 0,
    min_orf_length: int = 90,
    create_report: bool = False,
) -> dict[str, Any]:
    """Run only requested deterministic steps and preserve failure provenance."""
    results: dict[str, Any] = {}
    events: list[ExecutionEvent] = []

    def invoke(name: str, func: Any, parameters: dict[str, Any]) -> None:
        result = func(**parameters)
        results[name] = result.model_dump()
        events.append(ExecutionEvent(tool=name, status="completed" if result.ok else "failed", parameters={key: value for key, value in parameters.items() if key not in {"sequence", "sequence_a", "sequence_b"}}, message=(result.errors or [None])[0]))

    invoke("statistics", analyze_dna, {"sequence": primary_sequence})
    if not results["statistics"]["ok"]:
        return {"results": results, "execution": [event.model_dump() for event in events]}
    if mode in {"translation", "comprehensive"}:
        invoke("translation", translate_dna, {"sequence": primary_sequence, "frame": frame, "trim_incomplete_codon": True})
    if mode in {"orf", "comprehensive"}:
        invoke("orf", find_orfs, {"sequence": primary_sequence, "min_nt_length": min_orf_length})
    if mode in {"alignment", "comprehensive"}:
        if comparison_sequence:
            invoke("alignment", align_sequences, {"sequence_a": primary_sequence, "sequence_b": comparison_sequence})
        elif mode == "alignment":
            events.append(ExecutionEvent(tool="alignment", status="skipped", message="A comparison sequence is required."))
    if create_report:
        report = generate_report(results)
        results["report"] = {"ok": True, "tool": "generate_report", "data": {key: report[key] for key in ("json", "csv", "html")}, "warnings": [], "errors": []}
        events.append(ExecutionEvent(tool="generate_report", status="completed"))
    return {"results": results, "execution": [event.model_dump() for event in events]}

