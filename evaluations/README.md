# BioPilot evaluation suite

Run `py -m pytest tests -q` for deterministic offline evaluations. The workflow tests
cover requested tool selection, structured output, report generation, failure honesty,
and no-network behavior when NCBI configuration is absent. Agent model-response
evaluation requires a configured `GOOGLE_API_KEY` and is deliberately separate because
it makes an external model request.

Representative prompts are recorded in `cases.json` for manual or future ADK evaluation:
GC content, translation/frame, pairwise comparison, ORF discovery, invalid data,
reporting, error honesty, and scientific limitations.

