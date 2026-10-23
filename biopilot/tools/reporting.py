"""Safe JSON, CSV, and HTML report generation from actual structured results."""

from __future__ import annotations

import csv
import html
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from Bio import __version__ as biopython_version

from biopilot import __version__
from biopilot.config import get_settings


def generate_report(results: dict[str, Any], title: str = "BioPilot Analysis Report") -> dict[str, Any]:
    """Write JSON, flat CSV, and readable HTML reports beneath the reports directory."""
    output_dir = get_settings().reports_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_stem = re.sub(r"[^A-Za-z0-9_-]+", "_", title).strip("_")[:80] or "biopilot_report"
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    base = output_dir / f"{safe_stem}_{timestamp}"
    payload = {
        "title": title,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "tool_versions": {"biopilot": __version__, "biopython": biopython_version},
        "results": results,
        "scientific_limitations": "Results are computational analyses. Candidate ORFs and alignments require context and, where relevant, experimental validation.",
    }
    json_path = base.with_suffix(".json")
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    csv_path = base.with_suffix(".csv")
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["analysis", "ok", "warnings", "errors", "data_json"])
        for name, result in results.items():
            writer.writerow([name, result.get("ok", True), " | ".join(result.get("warnings", [])), " | ".join(result.get("errors", [])), json.dumps(result.get("data", {}), default=str)])
    html_path = base.with_suffix(".html")
    sections = "".join(
        f"<section><h2>{html.escape(name)}</h2><pre>{html.escape(json.dumps(value, indent=2, default=str))}</pre></section>"
        for name, value in results.items()
    )
    html_path.write_text(
        "<!doctype html><html><head><meta charset='utf-8'><title>"
        + html.escape(title)
        + "</title><style>body{font-family:system-ui;max-width:1100px;margin:2rem auto;padding:0 1rem}pre{white-space:pre-wrap;background:#f5f7fa;padding:1rem;border-radius:6px}section{border-top:1px solid #ddd}</style></head><body><h1>"
        + html.escape(title)
        + "</h1><p>Generated "
        + html.escape(payload["generated_at_utc"])
        + "</p>"
        + sections
        + "<footer><p>"
        + html.escape(payload["scientific_limitations"])
        + "</p></footer></body></html>",
        encoding="utf-8",
    )
    return {"json": str(json_path), "csv": str(csv_path), "html": str(html_path), "payload": payload}

