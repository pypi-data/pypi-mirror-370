"""MCP server exposing spec & feature resources and mutation tools."""
from __future__ import annotations
from typing import Optional, Literal
from mcp.server.fastmcp import FastMCP
from . import db

mcp = FastMCP("specs-mcp")

# Resources ----------------------------------------------------------------

@mcp.resource("spec://{spec_id}")
def spec_resource(spec_id: str) -> dict:
    """Return a single spec item (empty dict if not found)."""
    return db.get_spec(spec_id)

@mcp.resource("feature://{feature_key}")
def feature_resource(feature_key: str) -> dict:
    """Return a feature row (empty dict if not found)."""
    return db.get_feature(feature_key)

@mcp.tool()
def search_specs(status: Optional[str] = None, kind: Optional[str] = None, feature: Optional[str]=None) -> list[dict]:
    """Search specs (returns at most 500 items).

    Provide any combination of status, kind (REQUIREMENT|AC|NFR) and feature key.
    """
    return db.search_specs(status=status, kind=kind, feature=feature)

# Tools --------------------------------------------------------------------

@mcp.tool()
def record_verification(spec_id: str, outcome: Literal["PASSED","FAILED"], source: str = "", notes: str = "", occurred_at: Optional[str]=None) -> dict:
    """Record a verification event for a spec item and return insertion summary."""
    return db.record_event(spec_id=spec_id, outcome=outcome, source=source, notes=notes, occurred_at=occurred_at)

@mcp.tool()
def update_spec(
    spec_id: str,
    title: Optional[str] = None,
    statement: Optional[str] = None,
    rationale: Optional[str] = None,
    priority: Optional[str] = None,
    owner: Optional[str] = None,
    tags: Optional[str] = None,
    override_status: Optional[str] = None,
) -> dict:
    """Update mutable fields of a spec item and return the new row."""
    fields = {k: v for k, v in locals().items() if k not in {"spec_id"} and v is not None}
    return db.update_spec_fields(spec_id, fields)
