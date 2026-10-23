"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    """Application limits and optional external-service configuration."""

    google_api_key: str | None = None
    model_name: str = "gemini-2.5-flash"
    ncbi_email: str | None = None
    ncbi_api_key: str | None = None
    max_sequence_length: int = Field(default=1_000_000, ge=1)
    max_upload_bytes: int = Field(default=10_000_000, ge=1)
    max_records: int = Field(default=1_000, ge=1)
    reports_dir: Path = Path("reports")

    @property
    def has_agent_credentials(self) -> bool:
        return bool(self.google_api_key)

    @property
    def has_ncbi_credentials(self) -> bool:
        return bool(self.ncbi_email)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings without exposing secret values in logs."""
    import os

    return Settings(
        google_api_key=os.getenv("GOOGLE_API_KEY") or None,
        model_name=os.getenv("BIOPILOT_MODEL", "gemini-2.5-flash"),
        ncbi_email=os.getenv("NCBI_EMAIL") or None,
        ncbi_api_key=os.getenv("NCBI_API_KEY") or None,
    )

