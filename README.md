# BioPilot

BioPilot is a reproducible bioinformatics workbench with optional Google Agent
Development Kit (ADK) assistance. Local DNA analysis is performed by BioPython,
not an LLM: the model can choose constrained tools and explain their actual structured
outputs, but cannot run arbitrary code or invent calculations.

## Features

- DNA validation, literal-base GC percentage, composition, and reverse complement.
- Frame-aware translation with incomplete-codon and stop-codon reporting.
- Candidate start-to-stop ORF discovery on both strands (0-based, exclusive-end coordinates).
- Global/local `PairwiseAligner` comparison with an explicit identity denominator.
- Bounded FASTA/FASTQ parsing, including basic FASTQ quality summaries.
- JSON, CSV, and HTML reporting from completed structured tool results.
- Optional explicit NCBI Entrez searching and record retrieval.
- A Streamlit scientific workbench and a configured ADK root agent.

## Architecture

The local interface calls the deterministic workflow in
[analysis_workflow.py](biopilot/workflows/analysis_workflow.py). It validates inputs,
records each execution event, invokes BioPython tools, and optionally writes reports.
[agent.py](biopilot/agent.py) defines the ADK root agent separately; it exposes only
four narrow tool functions. See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for data flow
and trust boundaries.

## Prerequisites

- Windows PowerShell and Python 3.11+ (the checked environment used Python 3.13.1).
- An optional Gemini `GOOGLE_API_KEY` for runtime ADK model calls.
- An optional `NCBI_EMAIL` (and optionally `NCBI_API_KEY`) for external Entrez access.

## Install on Windows PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Populate only the variables required for features you intend to use. Do not commit
the resulting `.env` file.

## Run local analysis and UI

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run ui\app.py
# or from cmd.exe:
run_biopilot.bat
```

Try this first: **“Analyze this DNA sequence, calculate its GC content, find candidate
ORFs, and generate a report: ATGAAATAGGCGCGCATGCCCTAA”**. In the UI choose
**Comprehensive workflow**, then paste the sequence. It works without network access
or API keys. Sample records are in [demo_dna.fasta](data/samples/demo_dna.fasta).

## Configure ADK runtime

Set `GOOGLE_API_KEY` and optionally `BIOPILOT_MODEL` in `.env`; the default model is
`gemini-2.5-flash`. The root agent is the `root_agent` object in
[agent.py](biopilot/agent.py). Its construction and registered tool signatures are
tested offline, but an actual model invocation is intentionally not performed by the
test suite because it incurs an external authenticated request.

## Optional NCBI access

Set a real contact address in `NCBI_EMAIL` before calling the functions in
[ncbi.py](biopilot/tools/ncbi.py). NCBI operations are never selected by the offline
workflow and require explicit invocation. Network errors return structured failures;
they never become fabricated results.

## Tests and evaluation

```powershell
python -m pytest -q
```

The offline suite covers valid and invalid sequences, translation, ORFs, global/local
alignment, FASTA/FASTQ handling, no-credential NCBI behavior, workflow error handling,
report generation, and ADK agent construction. Prompt cases and instructions are in
[evaluations/README.md](evaluations/README.md).

## Scientific limitations

- Literal GC percent is `(G + C) / total characters * 100`; ambiguity codes remain in
  the denominator. BioPython's ambiguity-ignoring GC value is included separately.
- Translation and ORFs are computational results; they do not prove a functional
  protein or gene.
- Alignment score is distinct from percent identity and has no standalone clinical or
  evolutionary interpretation.
- Multiple uploaded records are summarized individually. This release does **not**
  claim to provide a multiple sequence alignment; configure a dedicated external
  aligner separately if that is required.
- NCBI records are external source data and require independent scientific judgment.

## Security and operational notes

Inputs are normalized and bounded, unsupported symbols fail explicitly, reports use
sanitized filenames below `reports/`, and no LLM is given a shell/code execution tool.
Uploaded sequences remain local unless the user deliberately invokes external NCBI or
an ADK runtime operation. Secrets are excluded by [.gitignore](.gitignore).

## Dependency summary

Pinned baseline runtime packages are BioPython 1.88, Google ADK 2.6.1, Streamlit
1.43.1, Pydantic 2.14.1, python-dotenv 1.0.1, and pytest 9.1.1; see
[requirements.txt](requirements.txt).

## Troubleshooting

- **`GOOGLE_API_KEY` missing**: Offline workbench functionality remains available;
  add the key only before model-backed ADK invocation.
- **NCBI request fails**: check `NCBI_EMAIL`, network connectivity, query/accession,
  and NCBI rate limits. Local tools remain independent.
- **Streamlit command missing**: activate the virtual environment and reinstall from
  [requirements.txt](requirements.txt).

