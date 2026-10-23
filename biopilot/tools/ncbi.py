"""Optional, explicitly invoked NCBI Entrez retrieval with bounded retries."""

from __future__ import annotations

import time
from pathlib import Path

from Bio import Entrez, SeqIO

from biopilot.config import get_settings
from biopilot.schemas.results import ToolResult


def search_ncbi(query: str, database: str = "nuccore", max_results: int = 5) -> ToolResult:
    """Search NCBI only after callers explicitly request external retrieval."""
    settings = get_settings()
    if not settings.ncbi_email:
        return ToolResult.failure("search_ncbi", "NCBI_EMAIL is required before contacting NCBI.")
    if not query.strip():
        return ToolResult.failure("search_ncbi", "NCBI search query is empty.")
    if not 1 <= max_results <= 20:
        return ToolResult.failure("search_ncbi", "max_results must be between 1 and 20.")
    Entrez.email, Entrez.api_key = settings.ncbi_email, settings.ncbi_api_key
    try:
        with Entrez.esearch(db=database, term=query.strip(), retmax=max_results) as handle:
            payload = Entrez.read(handle)
        ids = list(payload.get("IdList", []))
    except Exception as exc:
        return ToolResult.failure("search_ncbi", f"NCBI request failed: {type(exc).__name__}: {exc}")
    return ToolResult(
        tool="search_ncbi",
        data={"database": database, "query": query, "count": int(payload.get("Count", 0)), "ids": ids},
        warnings=["These identifiers and metadata were retrieved from NCBI; BioPilot has not independently validated their biological interpretation."],
        provenance={"source": "NCBI Entrez", "external_request": True},
    )


def fetch_ncbi_record(accession: str, database: str = "nuccore", record_format: str = "fasta") -> ToolResult:
    """Fetch a single FASTA or GenBank record from NCBI, with one bounded retry."""
    settings = get_settings()
    if not settings.ncbi_email:
        return ToolResult.failure("fetch_ncbi_record", "NCBI_EMAIL is required before contacting NCBI.")
    if not accession.strip() or any(char in accession for char in "\\/\x00"):
        return ToolResult.failure("fetch_ncbi_record", "Accession is empty or contains unsafe characters.")
    if record_format not in {"fasta", "gb", "genbank"}:
        return ToolResult.failure("fetch_ncbi_record", "record_format must be 'fasta' or 'genbank'.")
    Entrez.email, Entrez.api_key = settings.ncbi_email, settings.ncbi_api_key
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            with Entrez.efetch(db=database, id=accession.strip(), rettype="gb" if record_format in {"gb", "genbank"} else "fasta", retmode="text") as handle:
                record = SeqIO.read(handle, "genbank" if record_format in {"gb", "genbank"} else "fasta")
            return ToolResult(
                tool="fetch_ncbi_record",
                data={"id": record.id, "description": record.description, "length": len(record.seq), "sequence": str(record.seq), "annotations": dict(record.annotations) if record_format in {"gb", "genbank"} else {}},
                provenance={"source": "NCBI Entrez", "accession": accession, "external_request": True},
            )
        except Exception as exc:
            last_error = exc
            if attempt == 0:
                time.sleep(0.34)
    return ToolResult.failure("fetch_ncbi_record", f"NCBI retrieval failed after bounded retry: {type(last_error).__name__}: {last_error}")

