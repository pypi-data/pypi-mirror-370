from __future__ import annotations
import sqlite3, threading, os
from pathlib import Path
from datetime import datetime
from typing import Any, Iterable, Sequence, List, Dict, Set
import uuid

DB_PATH = Path(os.environ.get("SPEC_MCP_DB", Path(__file__).parent / "data" / "specs.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
_lock = threading.RLock()

def _connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

_conn = _connect()

STATUSES = ("UNTESTED","FAILING","PARTIAL","VERIFIED")

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec='seconds') + 'Z'

def ensure_schema(reset: bool=False):
    with _lock:
        cur = _conn.cursor()
        if reset:
            cur.executescript("DROP TABLE IF EXISTS verification_event;DROP TABLE IF EXISTS spec_item;DROP TABLE IF EXISTS feature;")
        cur.executescript(
            """
            PRAGMA foreign_keys=ON;
                        CREATE TABLE IF NOT EXISTS feature (
                            feature_key TEXT PRIMARY KEY,
                            name TEXT NOT NULL,
                            doc_path TEXT,
                            status TEXT NOT NULL CHECK(status IN ('UNTESTED','FAILING','PARTIAL','VERIFIED')) DEFAULT 'UNTESTED',
                            override_status TEXT CHECK(override_status IN ('UNTESTED','FAILING','PARTIAL','VERIFIED')),
                            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE TABLE IF NOT EXISTS spec_item (
                            id TEXT PRIMARY KEY,
                            feature_key TEXT NOT NULL REFERENCES feature(feature_key) ON DELETE CASCADE,
                            kind TEXT NOT NULL CHECK(kind IN ('REQUIREMENT','AC','NFR')),
                            title TEXT,
                            statement TEXT NOT NULL,
                            rationale TEXT,
                            priority TEXT,
                            owner TEXT,
                            tags TEXT,
                            parent_id TEXT REFERENCES spec_item(id) ON DELETE CASCADE,
                            status TEXT NOT NULL CHECK(status IN ('UNTESTED','FAILING','PARTIAL','VERIFIED')) DEFAULT 'UNTESTED',
                            override_status TEXT CHECK(override_status IN ('UNTESTED','FAILING','PARTIAL','VERIFIED')),
                            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                        );
            CREATE TABLE IF NOT EXISTS verification_event (
              id TEXT PRIMARY KEY,
              spec_id TEXT NOT NULL REFERENCES spec_item(id) ON DELETE CASCADE,
              outcome TEXT NOT NULL CHECK(outcome IN ('PASSED','FAILED')),
              occurred_at TEXT NOT NULL,
              source TEXT,
              notes TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_spec_feature_kind ON spec_item(feature_key, kind);
            CREATE INDEX IF NOT EXISTS idx_spec_parent ON spec_item(parent_id);
            CREATE INDEX IF NOT EXISTS idx_event_spec_time ON verification_event(spec_id, occurred_at);
            """
        )
        _conn.commit()
        # Backfill override columns if tables already existed
        for (tbl,col) in [('feature','override_status'),('spec_item','override_status')]:
            cur.execute("PRAGMA table_info(%s)" % tbl)
            cols = [r[1] for r in cur.fetchall()]
            if col not in cols:
                try:
                    cur.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} TEXT CHECK({col} IN ('UNTESTED','FAILING','PARTIAL','VERIFIED'))")
                except Exception:
                    pass
        _conn.commit()

def execute(sql: str, params: Iterable[Any] = ()):  # write
    with _lock:
        cur = _conn.cursor()
        cur.execute(sql, params)
        _conn.commit()
        return cur

def executemany(sql: str, seq: Sequence[Iterable[Any]]):
    with _lock:
        cur = _conn.cursor()
        cur.executemany(sql, seq)
        _conn.commit()
        return cur

def query(sql: str, params: Iterable[Any] = ()):  # read many
    with _lock:
        cur = _conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

def query_one(sql: str, params: Iterable[Any] = ()):  # read one
    rows = query(sql, params)
    return rows[0] if rows else None

def new_uuid() -> str:
    return uuid.uuid4().hex

def latest_event(spec_id: str):
    return query_one("SELECT outcome, occurred_at FROM verification_event WHERE spec_id=? ORDER BY occurred_at DESC LIMIT 1", (spec_id,))

def leaf_effective_status(spec_id: str) -> str:
    ev = latest_event(spec_id)
    if not ev:
        return 'UNTESTED'
    return 'VERIFIED' if ev['outcome'] == 'PASSED' else 'FAILING'

def recompute_requirement(req_id: str):
    # Gather children AC & NFR
    children = query("SELECT id, kind, status FROM spec_item WHERE parent_id=?", (req_id,))
    # If requirement has direct events treat as virtual leaf
    virtual_leaf_status = leaf_effective_status(req_id)
    leaf_statuses = [leaf_effective_status(c['id']) for c in children if c['kind'] in ('AC','NFR')]
    # Include virtual leaf only if it has events
    if latest_event(req_id):
        leaf_statuses.append(virtual_leaf_status)
    status = roll_up_status(leaf_statuses)
    execute("UPDATE spec_item SET status=?, updated_at=? WHERE id=?", (status, now_iso(), req_id))
    # Recompute feature
    req = query_one("SELECT feature_key FROM spec_item WHERE id=?", (req_id,))
    if req:
        recompute_feature(req['feature_key'])

def recompute_feature(feature_key: str):
    # children requirements + top-level NFR (parent_id null and kind NFR)
    items = query("SELECT status, kind FROM spec_item WHERE feature_key=? AND (kind='REQUIREMENT' OR (kind='NFR' AND parent_id IS NULL))", (feature_key,))
    statuses = [i['status'] for i in items]
    status = roll_up_status(statuses)
    execute("UPDATE feature SET status=?, updated_at=? WHERE feature_key=?", (status, now_iso(), feature_key))

def roll_up_status(statuses: list[str]) -> str:
    if not statuses:
        return 'UNTESTED'
    if any(s == 'FAILING' for s in statuses):
        return 'FAILING'
    if all(s == 'VERIFIED' for s in statuses):
        return 'VERIFIED'
    if any(s == 'VERIFIED' for s in statuses) and not any(s == 'FAILING' for s in statuses):
        return 'PARTIAL'
    return 'UNTESTED'

def recompute_all():
    reqs = query("SELECT id FROM spec_item WHERE kind='REQUIREMENT'")
    for r in reqs:
        recompute_requirement(r['id'])
    feats = query("SELECT feature_key FROM feature")
    for f in feats:
        recompute_feature(f['feature_key'])

def status_counts() -> Dict[str,int]:
    rows = query("SELECT status, COUNT(*) as c FROM spec_item GROUP BY status")
    result = {s:0 for s in STATUSES}
    for r in rows:
        result[r['status']] = r['c']
    return result

def effective_status(base: str, override: str|None) -> str:
    return override or base

def load_feature(feature_key: str):
    return query_one("SELECT feature_key,name,status,override_status,updated_at FROM feature WHERE feature_key=?", (feature_key,))

def load_spec(spec_id: str):
    return query_one("SELECT id,feature_key,kind,title,statement,status,override_status,parent_id,updated_at FROM spec_item WHERE id=?", (spec_id,))

def patch_feature(feature_key: str, name: str|None=None, override_status: str|None=None, clear_override: bool=False):
    row = load_feature(feature_key)
    if not row:
        return None
    fields = []
    params: list[Any] = []
    if name is not None:
        fields.append('name=?'); params.append(name)
    if clear_override:
        fields.append('override_status=NULL')
    elif override_status is not None:
        if override_status not in STATUSES:
            raise ValueError('invalid status')
        fields.append('override_status=?'); params.append(override_status)
    if not fields:
        return row
    fields.append('updated_at=?'); params.append(now_iso())
    params.append(feature_key)
    execute(f"UPDATE feature SET {', '.join(fields)} WHERE feature_key=?", params)
    return load_feature(feature_key)

def patch_spec(
    spec_id: str,
    title: str|None=None,
    statement: str|None=None,
    rationale: str|None=None,
    priority: str|None=None,
    owner: str|None=None,
    tags: str|None=None,
    override_status: str|None=None,
    clear_override: bool=False,
):
    row = load_spec(spec_id)
    if not row:
        return None
    fields=[]; params: list[Any]=[]
    if title is not None:
        fields.append('title=?'); params.append(title)
    if statement is not None:
        fields.append('statement=?'); params.append(statement)
    if rationale is not None:
        fields.append('rationale=?'); params.append(rationale)
    if priority is not None:
        fields.append('priority=?'); params.append(priority)
    if owner is not None:
        fields.append('owner=?'); params.append(owner)
    if tags is not None:
        fields.append('tags=?'); params.append(tags)
    # Allow override only for REQUIREMENT or NFR
    if clear_override:
        fields.append('override_status=NULL')
    elif override_status is not None:
        if override_status not in STATUSES:
            raise ValueError('invalid status')
        if row['kind'] == 'AC':
            raise ValueError('cannot override AC status')
        fields.append('override_status=?'); params.append(override_status)
    if not fields:
        return row
    fields.append('updated_at=?'); params.append(now_iso()); params.append(spec_id)
    execute(f"UPDATE spec_item SET {', '.join(fields)} WHERE id=?", params)
    # If leaf changed text no status change; if override added/cleared recompute upward if requirement or leaf nfr
    updated = load_spec(spec_id)
    if updated['kind'] == 'REQUIREMENT':
        recompute_requirement(spec_id)
    elif updated['kind'] in ('AC','NFR') and updated['parent_id']:
        recompute_requirement(updated['parent_id'])
    else:
        recompute_feature(updated['feature_key'])
    return load_spec(spec_id)

def insert_events(events: List[Dict[str,Any]]):
    """Insert multiple verification events. Each event dict requires: spec_id, outcome, optional occurred_at/source/notes.
    After insertion, recompute relevant hierarchy nodes efficiently."""
    if not events:
        return {"inserted":0}
    now = now_iso()
    rows_to_insert = []
    affected_specs: Set[str] = set()
    for e in events:
        spec_id = e.get('spec_id')
        outcome = e.get('outcome')
        if outcome not in ('PASSED','FAILED'):
            continue
        spec = query_one("SELECT id, kind, parent_id, feature_key FROM spec_item WHERE id=?", (spec_id,))
        if not spec:
            continue
        occurred_at = e.get('occurred_at') or now
        rows_to_insert.append((new_uuid(), spec_id, outcome, occurred_at, e.get('source'), e.get('notes')))
        affected_specs.add(spec_id)
    if rows_to_insert:
        executemany("INSERT INTO verification_event (id,spec_id,outcome,occurred_at,source,notes) VALUES (?,?,?,?,?,?)", rows_to_insert)
    # Recompute: for each leaf spec inserted, propagate up
    for spec_id in affected_specs:
        spec = query_one("SELECT id, kind, parent_id, feature_key FROM spec_item WHERE id=?", (spec_id,))
        if not spec:
            continue
        if spec['kind'] in ('AC','NFR'):
            # update leaf itself
            leaf_status = leaf_effective_status(spec_id)
            execute("UPDATE spec_item SET status=?, updated_at=? WHERE id=?", (leaf_status, now_iso(), spec_id))
            if spec['parent_id']:
                recompute_requirement(spec['parent_id'])
            else:
                recompute_feature(spec['feature_key'])
        elif spec['kind'] == 'REQUIREMENT':
            recompute_requirement(spec_id)
    return {"inserted": len(rows_to_insert)}

def events_for_spec(spec_id: str, limit: int=50):
    return query("SELECT outcome, occurred_at, source, notes FROM verification_event WHERE spec_id=? ORDER BY occurred_at DESC LIMIT ?", (spec_id, limit))

ensure_schema(reset=os.environ.get('SPEC_MCP_RESET','0')=='1')
