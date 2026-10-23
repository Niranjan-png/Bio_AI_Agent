"""Google ADK root agent configured exclusively with constrained BioPilot tools."""

from __future__ import annotations

from typing import Any

from google.adk.agents import Agent

from biopilot.config import get_settings
from biopilot.tools.alignment import align_sequences
from biopilot.tools.orf_analysis import find_orfs
from biopilot.tools.sequence_analysis import analyze_dna, translate_dna

INSTRUCTION = """You are BioPilot, a careful bioinformatics research assistant.
Use a registered tool for every numerical sequence analysis; never estimate or invent
calculations. Validate tool result `ok` before relying on it. Explain which tools ran,
their actual outputs, parameters, warnings, and any failed or omitted analyses.
Candidate ORFs are predictions, translations do not prove function, and alignment
scores are not percent identity. Do not claim clinical, evolutionary, or experimental
significance without evidence. Do not execute code, shell commands, or unregistered
operations. For local DNA statistics, translation, ORF discovery, and pairwise
comparison use the corresponding deterministic tool. Ask for a sequence when absent.
Return readable scientific prose grounded only in tool outputs."""


def dna_statistics_tool(sequence: str) -> dict[str, Any]:
    """Calculate validated DNA length, base counts, GC percent, and reverse complement."""
    return analyze_dna(sequence).model_dump()


def dna_translation_tool(sequence: str, frame: int = 0, genetic_code: int = 1) -> dict[str, Any]:
    """Translate validated DNA in frame 0, 1, or 2; trims only trailing incomplete codons."""
    return translate_dna(sequence, frame=frame, genetic_code=genetic_code, trim_incomplete_codon=True).model_dump()


def orf_discovery_tool(sequence: str, min_nt_length: int = 90, include_reverse: bool = True) -> dict[str, Any]:
    """Find candidate start-to-stop ORFs on forward and optionally reverse strands."""
    return find_orfs(sequence, min_nt_length=min_nt_length, include_reverse=include_reverse).model_dump()


def pairwise_alignment_tool(sequence_a: str, sequence_b: str, mode: str = "global") -> dict[str, Any]:
    """Globally or locally align two validated DNA sequences with documented identity."""
    return align_sequences(sequence_a, sequence_b, mode=mode).model_dump()


def create_root_agent() -> Agent:
    """Create an ADK agent; runtime invocation additionally needs GOOGLE_API_KEY."""
    settings = get_settings()
    return Agent(
        name="biopilot",
        model=settings.model_name,
        description="Tool-using bioinformatics assistant for validated local DNA analysis.",
        instruction=INSTRUCTION,
        tools=[dna_statistics_tool, dna_translation_tool, orf_discovery_tool, pairwise_alignment_tool],
    )


root_agent = create_root_agent()

