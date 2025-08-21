"""MCP resource handlers (read-only textual views)."""
from __future__ import annotations
from . import db
from .app import app
from .queries import feature_rows, spec_row

@app.resource("mcp://specs/features")
async def list_features() -> str:
    out = []
    for r in feature_rows():
        out.append(
            f"{r['feature_key']}: {r['status']} (V:{r['verified_count']} F:{r['failing_count']} U:{r['untested_count']} P:{r['partial_count']})"
        )
    return "\n".join(out)

@app.resource("mcp://specs/feature/{feature_key}")
async def feature_detail(feature_key: str) -> str:
    feat = db.query_one("SELECT * FROM feature WHERE feature_key=?", (feature_key,))
    if not feat:
        return "NOT FOUND"
    reqs = db.query(
        "SELECT id,title,status FROM spec_item WHERE feature_key=? AND kind='REQUIREMENT' ORDER BY id",
        (feature_key,),
    )
    lines = [f"Feature {feat['feature_key']} {feat['name']} - {feat['status']}"]
    for r in reqs:
        children = db.query(
            "SELECT id,status,kind FROM spec_item WHERE parent_id=? ORDER BY id", (r['id'],)
        )
        lines.append(
            f"  - {r['id']} {r['title']} [{r['status']}] ({len(children)} leaves)"
        )
        for c in children:
            lines.append(f"      * {c['id']} [{c['kind']}] {c['status']}")
    return "\n".join(lines)

@app.resource("mcp://specs/spec/{spec_id}")
async def spec_detail(spec_id: str) -> str:
    row = spec_row(spec_id)
    if not row:
        return "NOT FOUND"
    events = db.query(
        "SELECT outcome,occurred_at,source FROM verification_event WHERE spec_id=? ORDER BY occurred_at DESC LIMIT 10",
        (spec_id,),
    )
    lines = [
        f"{row['id']} ({row['kind']}) - {row['status']}",
        row['statement'],
        "Events:",
    ]
    for e in events:
        lines.append(
            f"  {e['occurred_at']} {e['outcome']} {e['source'] or ''}"
        )
    return "\n".join(lines)
