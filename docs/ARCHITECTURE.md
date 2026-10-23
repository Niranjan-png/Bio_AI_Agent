# BioPilot architecture

## Components and data flow

1. The Streamlit layer in [app.py](../ui/app.py) accepts untrusted text or uploaded
   FASTA/FASTQ data, displays execution status, and never exposes environment secrets.
2. [validation.py](../biopilot/tools/validation.py) normalizes bounded DNA input and
   rejects invalid symbols before deterministic analysis.
3. BioPython tools in [tools](../biopilot/tools/) return the uniform `ToolResult`
   structure: `ok`, data, warnings, errors, and provenance.
4. [analysis_workflow.py](../biopilot/workflows/analysis_workflow.py) provides ordered
   offline orchestration and preserves an execution ledger. It never makes a network
   request for a local calculation.
5. [reporting.py](../biopilot/tools/reporting.py) writes JSON, CSV, and HTML from
   already-produced results into a restricted reports directory.
6. [agent.py](../biopilot/agent.py) is the independent Google ADK integration. It can
   interpret language and call registered functions but has no arbitrary shell, Python,
   SQL, or network-execution tool.

## Trust boundaries

Sequence text, files, prompts, and external NCBI responses are untrusted. Validation
and file limits run before analysis. NCBI is optional and only called directly; its
returned content is marked as external provenance. A Gemini key, when configured, is
used only by the ADK runtime and is not displayed, logged, or included in reports.

## Determinism

The same sequence and parameters produce the same local calculations. A report stores
tool outputs, warnings, dependency versions, and the parameters included by the
workflow's execution events. Model prose is supplementary and must be grounded in
those structured outputs.

