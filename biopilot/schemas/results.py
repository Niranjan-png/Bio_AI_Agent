"""Structured, JSON-safe tool result schemas."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Uniform successful or failed result returned by every public tool."""

    ok: bool = True
    tool: str
    data: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def failure(cls, tool: str, message: str) -> "ToolResult":
        return cls(ok=False, tool=tool, errors=[message])


class ExecutionEvent(BaseModel):
    """One workflow action retained for reproducibility."""

    tool: str
    status: Literal["completed", "failed", "skipped"]
    parameters: dict[str, Any] = Field(default_factory=dict)
    message: str | None = None

