"""Streamlit scientific workbench for offline BioPilot workflows."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from biopilot.config import get_settings
from biopilot.tools.sequence_io import parse_sequence_file
from biopilot.workflows.analysis_workflow import run_analysis

st.set_page_config(page_title="BioPilot", page_icon="🧬", layout="wide")
st.title("🧬 BioPilot")
st.caption("A local, reproducible bioinformatics workbench powered by BioPython. AI agent calls are optional.")

SAMPLE = "ATGAAATAGGCGCGCATGCCCTAA"
with st.sidebar:
    st.header("Analysis controls")
    mode_label = st.selectbox("Analysis mode", ["Comprehensive workflow", "Sequence statistics", "Translation", "ORF discovery", "Pairwise alignment"])
    mode = {"Comprehensive workflow": "comprehensive", "Sequence statistics": "statistics", "Translation": "translation", "ORF discovery": "orf", "Pairwise alignment": "alignment"}[mode_label]
    frame = st.selectbox("Translation frame", [0, 1, 2], format_func=lambda value: f"+{value + 1}")
    min_orf_length = st.number_input("Minimum ORF length (nt)", min_value=3, value=90, step=3)
    create_report = st.checkbox("Generate JSON, CSV, and HTML report", value=True)
    if st.button("Load sample DNA"):
        st.session_state.primary = SAMPLE

request = st.text_area("Natural-language request (recorded for context; offline mode uses the selected analysis)", placeholder="Analyze this DNA sequence, identify candidate ORFs, and generate a report.")
primary = st.text_area("Primary DNA sequence", key="primary", height=150, placeholder="Paste IUPAC DNA here")
comparison = st.text_area("Comparison DNA sequence", height=100, placeholder="Required for pairwise alignment")
upload = st.file_uploader("Upload FASTA or FASTQ", type=["fa", "fasta", "fna", "fq", "fastq"])

if upload is not None:
    parsed = parse_sequence_file(upload.getvalue(), upload.name)
    if parsed.ok:
        records = parsed.data["records"]
        st.success(f"Parsed {len(records)} {parsed.data['format'].upper()} record(s) locally.")
        st.dataframe(pd.DataFrame([{key: value for key, value in record.items() if key != "sequence"} for record in records]), use_container_width=True)
        if not primary and records:
            primary = str(records[0]["sequence"])
    else:
        st.error("; ".join(parsed.errors))

if st.button("Run analysis", type="primary"):
    if not primary:
        st.error("Enter a primary DNA sequence or upload a valid sequence file.")
    else:
        with st.status("Running deterministic BioPython tools…", expanded=True) as status:
            outcome = run_analysis(primary, mode, comparison or None, frame=frame, min_orf_length=int(min_orf_length), create_report=create_report)
            status.update(label="Analysis complete", state="complete")
        st.subheader("Execution status")
        st.dataframe(pd.DataFrame(outcome["execution"]), use_container_width=True)
        for name, result in outcome["results"].items():
            with st.expander(name.replace("_", " ").title(), expanded=name == "statistics"):
                if not result.get("ok", True):
                    st.error("; ".join(result.get("errors", [])))
                else:
                    st.json(result.get("data", {}))
                for warning in result.get("warnings", []):
                    st.warning(warning)
        report = outcome["results"].get("report", {}).get("data", {})
        if report:
            st.subheader("Downloads")
            for fmt, report_path in report.items():
                path = Path(report_path)
                if path.exists():
                    st.download_button(f"Download {fmt.upper()}", path.read_bytes(), file_name=path.name)
        if request:
            st.info("The natural-language request was not sent externally. Configure GOOGLE_API_KEY and use the ADK root agent separately for model-guided tool selection.")

settings = get_settings()
st.divider()
st.caption("Local analysis remains local. " + ("ADK runtime credentials are configured." if settings.has_agent_credentials else "GOOGLE_API_KEY is not configured; agent chat is unavailable, while offline analysis works."))

