from __future__ import annotations
from typing import Optional
from . import db

def record_verification(spec_id: str, outcome: str, source: Optional[str]=None, notes: Optional[str]=None, occurred_at: Optional[str]=None) -> dict:
    """Record PASSED/FAILED event for a spec item and recompute statuses.

    Shared by MCP tool layer and HTTP API to avoid circular imports.
    """
    row = db.query_one("SELECT * FROM spec_item WHERE id=?", (spec_id,))
    if not row:
        return {"error": "spec not found"}
    if outcome not in ("PASSED", "FAILED"):
        return {"error": "invalid outcome"}
    now_fn = getattr(db, 'now_iso', None)
    new_uuid = getattr(db, 'new_uuid', None)
    leaf_status_fn = getattr(db, 'leaf_effective_status', None)
    recompute_req = getattr(db, 'recompute_requirement', None)
    recompute_feat = getattr(db, 'recompute_feature', None)
    when = occurred_at or (now_fn() if now_fn else '')
    if not new_uuid:
        import uuid
        new_uuid = lambda: str(uuid.uuid4())  # type: ignore
    db.execute(
        "INSERT INTO verification_event (id,spec_id,outcome,occurred_at,source,notes) VALUES (?,?,?,?,?,?)",
        (new_uuid(), spec_id, outcome, when, source, notes),
    )
    kind = row['kind']
    if kind in ('AC', 'NFR') and leaf_status_fn:
        new_status = leaf_status_fn(spec_id)
        db.execute(
            "UPDATE spec_item SET status=?, updated_at=? WHERE id=?",
            (new_status, now_fn() if now_fn else '', spec_id),
        )
        parent = row['parent_id']
        if parent and recompute_req:
            recompute_req(parent)
        elif recompute_feat:
            recompute_feat(row['feature_key'])
    elif kind == 'REQUIREMENT' and recompute_req:
        recompute_req(spec_id)
    updated = db.query_one("SELECT id,status FROM spec_item WHERE id=?", (spec_id,))
    return {"id": updated['id'], "status": updated['status']}
