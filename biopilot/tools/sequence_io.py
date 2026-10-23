"""Bounded FASTA/FASTQ parsing and safe selected-record export."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from Bio import SeqIO

from biopilot.config import get_settings
from biopilot.schemas.results import ToolResult


def parse_sequence_file(content: bytes, filename: str) -> ToolResult:
    """Parse bounded FASTA or FASTQ bytes; extension is not trusted by itself."""
    settings = get_settings()
    suffix = Path(filename).suffix.lower()
    formats = {".fa": "fasta", ".fasta": "fasta", ".fna": "fasta", ".fq": "fastq", ".fastq": "fastq"}
    file_format = formats.get(suffix)
    if not file_format:
        return ToolResult.failure("parse_sequence_file", "Unsupported format. Use FASTA (.fa/.fasta/.fna) or FASTQ (.fq/.fastq).")
    if not content:
        return ToolResult.failure("parse_sequence_file", "Input file is empty.")
    if len(content) > settings.max_upload_bytes:
        return ToolResult.failure("parse_sequence_file", "Input file exceeds configured upload size limit.")
    try:
        text = content.decode("utf-8")
        records = list(SeqIO.parse(StringIO(text), file_format))
    except (UnicodeDecodeError, ValueError) as exc:
        return ToolResult.failure("parse_sequence_file", f"Malformed {file_format.upper()} input: {exc}")
    if not records:
        return ToolResult.failure("parse_sequence_file", f"No {file_format.upper()} records were found.")
    if len(records) > settings.max_records:
        return ToolResult.failure("parse_sequence_file", "Record count exceeds configured limit.")
    summaries = []
    for record in records:
        item: dict[str, object] = {"id": record.id, "description": record.description, "sequence": str(record.seq).upper(), "length": len(record.seq)}
        if file_format == "fastq":
            qualities = record.letter_annotations.get("phred_quality", [])
            item["quality"] = {"min": min(qualities) if qualities else None, "max": max(qualities) if qualities else None, "mean": round(sum(qualities) / len(qualities), 3) if qualities else None}
        summaries.append(item)
    return ToolResult(tool="parse_sequence_file", data={"format": file_format, "record_count": len(summaries), "records": summaries})

