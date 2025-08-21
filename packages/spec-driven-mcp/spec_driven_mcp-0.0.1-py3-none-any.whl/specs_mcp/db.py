"""Thin wrapper helpers mapping to existing spec_mcp.db module.

This isolates the minimal surface required by the MCP server so tools/resources
stay stable even if the underlying implementation evolves.
"""
from __future__ import annotations
from typing import Optional, Iterable
from spec_mcp import db as core

# Re-export ensure_schema so an external process can initialize.
ensure_schema = core.ensure_schema

# Basic getters ------------------------------------------------------------

def get_spec(spec_id: str) -> dict:
    row = core.load_spec(spec_id)
    return dict(row) if row else {}

def get_feature(feature_key: str) -> dict:
    row = core.load_feature(feature_key)
    return dict(row) if row else {}

# Search -------------------------------------------------------------------

def search_specs(status: Optional[str]=None, kind: Optional[str]=None, feature: Optional[str]=None) -> list[dict]:
    clauses = []
    params: list[str] = []
    if status:
        clauses.append("status=?")
        params.append(status)
    if kind:
        clauses.append("kind=?")
        params.append(kind)
    if feature:
        clauses.append("feature_key=?")
        params.append(feature)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    rows = core.query(f"SELECT id, feature_key, kind, title, statement, status, override_status, updated_at FROM spec_item {where} ORDER BY id LIMIT 500", params)
    return [dict(r) for r in rows]

# Events / updates ---------------------------------------------------------

def record_event(spec_id: str, outcome: str, source: str = "", notes: str = "", occurred_at: Optional[str]=None):
    # reuse insert_events for consistency
    ev = {"spec_id": spec_id, "outcome": outcome, "source": source or None, "notes": notes or None}
    if occurred_at:
        ev["occurred_at"] = occurred_at
    return core.insert_events([ev])

def update_spec_fields(spec_id: str, fields: dict) -> dict:
    # Map to patch_spec supported params
    patch_args = {k: fields[k] for k in ["title","statement","rationale","priority","owner","tags","override_status"] if k in fields}
    updated = core.patch_spec(spec_id, **patch_args)
    return dict(updated) if updated else {}
