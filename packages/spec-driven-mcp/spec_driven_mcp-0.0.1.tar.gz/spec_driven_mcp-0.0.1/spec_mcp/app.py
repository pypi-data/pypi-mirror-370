"""MCP FastMCP app and tools registration."""
from __future__ import annotations
from typing import Optional
from mcp.server.fastmcp import FastMCP
from .verification import record_verification as _record_verification_impl

app = FastMCP("spec-driven-mcp")

@app.tool()
def record_verification(spec_id: str, outcome: str, source: Optional[str]=None, notes: Optional[str]=None, occurred_at: Optional[str]=None) -> dict:
    """Record verification outcome for a spec item (PASSED/FAILED)."""
    return _record_verification_impl(spec_id, outcome, source=source, notes=notes, occurred_at=occurred_at)
