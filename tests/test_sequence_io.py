from biopilot.tools.sequence_io import parse_sequence_file


def test_fasta_and_fastq_parsing() -> None:
    fasta = parse_sequence_file(b">a first\nACGT\n>b\nNN\n", "input.fasta")
    assert fasta.ok and fasta.data["record_count"] == 2
    fastq = parse_sequence_file(b"@read\nACGT\n+\nIIII\n", "reads.fastq")
    assert fastq.ok and fastq.data["records"][0]["quality"]["mean"] == 40.0


def test_rejects_empty_malformed_and_unknown_files() -> None:
    assert not parse_sequence_file(b"", "empty.fa").ok
    assert not parse_sequence_file(b"not fasta", "bad.fasta").ok
    assert not parse_sequence_file(b">a\nACGT", "input.txt").ok

