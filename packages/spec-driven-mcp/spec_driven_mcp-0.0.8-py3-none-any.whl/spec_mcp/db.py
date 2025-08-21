from __future__ import annotations
import sqlite3, threading, os
from pathlib import Path
from datetime import datetime
from typing import Any, Iterable, Sequence, List, Dict, Set, Optional
import uuid

def default_db_path() -> str:
    """Return the database path using a robust, cross-platform strategy.
    
    Priority order:
    1. SPEC_MCP_DB_PATH environment variable (explicit database file path)
    2. Current working directory (project-local): <cwd>/.spec-mcp/specs.db
    3. User data directory as fallback
    
    Returns:
        Absolute path to the database file
    """
    import platformdirs
    
    # 1. Check for explicit database file path override
    env_db_path = os.getenv("SPEC_MCP_DB_PATH")
    if env_db_path:
        db_path = Path(env_db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return str(db_path)
    
    # 2. Use project-local database in current working directory
    # This works well for MCP servers launched from project directories
    try:
        cwd = Path.cwd()
        db_path = cwd / ".spec-mcp" / "specs.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return str(db_path)
    except (OSError, PermissionError):
        # Fall through to user data directory if we can't write to cwd
        pass
    
    # 3. Fallback to user data directory
    # This ensures consistent behavior when current directory is not writable
    user_data_dir = platformdirs.user_data_dir("spec-mcp", "SpecMCP")
    db_path = Path(user_data_dir) / "specs.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return str(db_path)

# Defer DB_PATH computation until first access to allow for runtime configuration
_db_path_cache = None

def get_db_path() -> Path:
    """Get the database path, computing it lazily on first access."""
    global _db_path_cache
    if _db_path_cache is None:
        _db_path_cache = Path(default_db_path())
    return _db_path_cache

def reset_db_path_cache():
    """Reset the database path cache to force recomputation."""
    global _db_path_cache
    _db_path_cache = None

def reset_connection_cache():
    """Reset the database connection cache to force reconnection."""
    global _conn
    if _conn is not None:
        try:
            _conn.close()
        except Exception:
            pass  # Ignore errors when closing
        _conn = None

def reset_all_caches():
    """Reset both database path and connection caches."""
    reset_db_path_cache()
    reset_connection_cache()

# Create a module-level property-like object
class _DBPathProperty:
    def __str__(self):
        return str(get_db_path())
    
    def __fspath__(self):
        return str(get_db_path())
    
    def __repr__(self):
        return f"DBPath({get_db_path()})"

DB_PATH = _DBPathProperty()
_lock = threading.RLock()

def _connect():
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Defer connection until first access
_conn = None

def get_connection():
    """Get database connection, creating it lazily."""
    global _conn
    if _conn is None:
        _conn = _connect()
    return _conn

STATUSES = ("UNTESTED","FAILING","PARTIAL","VERIFIED")

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec='seconds') + 'Z'

def ensure_schema(reset: bool=False):
    with _lock:
        cur = get_connection().cursor()
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
                            title TEXT, -- optional short title
                            description TEXT NOT NULL,
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
        get_connection().commit()
        # Backfill override columns if tables already existed
        for (tbl,col) in [('feature','override_status'),('spec_item','override_status')]:
            cur.execute("PRAGMA table_info(%s)" % tbl)
            cols = [r[1] for r in cur.fetchall()]
            if col not in cols:
                try:
                    cur.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} TEXT CHECK({col} IN ('UNTESTED','FAILING','PARTIAL','VERIFIED'))")
                except Exception:
                    pass
        # Add title column if missing
        cur.execute("PRAGMA table_info(spec_item)")
        if 'title' not in [r[1] for r in cur.fetchall()]:
            try:
                cur.execute("ALTER TABLE spec_item ADD COLUMN title TEXT")
            except Exception:
                pass
        get_connection().commit()

def execute(sql: str, params: Iterable[Any] = ()):  # write
    with _lock:
        cur = get_connection().cursor()
        cur.execute(sql, params)
        get_connection().commit()
        return cur

def executemany(sql: str, seq: Sequence[Iterable[Any]]):
    with _lock:
        cur = get_connection().cursor()
        cur.executemany(sql, seq)
        get_connection().commit()
        return cur

def query(sql: str, params: Iterable[Any] = ()):  # read many
    with _lock:
        cur = get_connection().cursor()
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
    return status

def ensure_sample_data():
    """Populate the database with illustrative sample data if empty.
    Idempotent: only runs when there are no features.
    """
    if query_one("SELECT feature_key FROM feature LIMIT 1"):
        return False
    now = now_iso()
    # Features
    execute("INSERT INTO feature (feature_key,name,status,updated_at) VALUES (?,?,?,?)", ("AUTH","Authentication & Login","UNTESTED", now))
    execute("INSERT INTO feature (feature_key,name,status,updated_at) VALUES (?,?,?,?)", ("PAY","Payments & Billing","UNTESTED", now))
    # Requirements AUTH
    executemany("INSERT INTO spec_item (id,feature_key,kind,description,parent_id,status,updated_at) VALUES (?,?,?,?,?,?,?)", [
        ("AUTH-REQ-LOGIN","AUTH","REQUIREMENT","User can log in with email/password",None,"UNTESTED",now),
        ("AUTH-REQ-RESET","AUTH","REQUIREMENT","User can reset password via email",None,"UNTESTED",now),
    ])
    # ACs for AUTH
    executemany("INSERT INTO spec_item (id,feature_key,kind,description,parent_id,status,updated_at) VALUES (?,?,?,?,?,?,?)", [
        ("AUTH-AC-LOGIN-SUCCESS","AUTH","AC","Valid credentials lead to dashboard","AUTH-REQ-LOGIN","UNTESTED",now),
        ("AUTH-AC-LOGIN-FAIL","AUTH","AC","Invalid password shows error","AUTH-REQ-LOGIN","UNTESTED",now),
        ("AUTH-AC-RESET-LINK","AUTH","AC","Reset email contains secure token","AUTH-REQ-RESET","UNTESTED",now),
    ])
    # NFR top-level for AUTH
    executemany("INSERT INTO spec_item (id,feature_key,kind,description,parent_id,status,updated_at) VALUES (?,?,?,?,?,?,?)", [
        ("AUTH-NFR-LATENCY","AUTH","NFR","Auth requests P95 < 300ms",None,"UNTESTED",now),
    ])
    # Requirements PAY
    executemany("INSERT INTO spec_item (id,feature_key,kind,description,parent_id,status,updated_at) VALUES (?,?,?,?,?,?,?)", [
        ("PAY-REQ-CARD","PAY","REQUIREMENT","Process credit card payments",None,"UNTESTED",now),
        ("PAY-REQ-INVOICE","PAY","REQUIREMENT","Generate PDF invoices",None,"UNTESTED",now),
    ])
    # ACs for PAY
    executemany("INSERT INTO spec_item (id,feature_key,kind,description,parent_id,status,updated_at) VALUES (?,?,?,?,?,?,?)", [
        ("PAY-AC-CARD-VISA","PAY","AC","Accept valid VISA card","PAY-REQ-CARD","UNTESTED",now),
        ("PAY-AC-CARD-DECLINE","PAY","AC","Declined card returns failure","PAY-REQ-CARD","UNTESTED",now),
    ])
    # Orphan AC example
    execute("INSERT INTO spec_item (id,feature_key,kind,description,parent_id,status,updated_at) VALUES (?,?,?,?,?,?,?)", ("PAY-AC-ORPHAN","PAY","AC","Edge case orphan AC",None,"UNTESTED",now))
    # Top-level NFR for PAY
    execute("INSERT INTO spec_item (id,feature_key,kind,description,parent_id,status,updated_at) VALUES (?,?,?,?,?,?,?)", ("PAY-NFR-AVAIL","PAY","NFR","Payments uptime 99.9%",None,"UNTESTED",now))
    # Recompute statuses
    for fk in ("AUTH","PAY"):
        recompute_feature(fk)
    return True

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
    return query_one("SELECT id,feature_key,kind,title,description,status,override_status,parent_id,updated_at FROM spec_item WHERE id=?", (spec_id,))

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
    description: str|None=None,
    status: str|None=None,
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
    if description is not None:
        fields.append('description=?'); params.append(description)
    if priority is not None:
        fields.append('priority=?'); params.append(priority)
    if owner is not None:
        fields.append('owner=?'); params.append(owner)
    if tags is not None:
        fields.append('tags=?'); params.append(tags)
    # Update base status only for AC / NFR (not requirements which are rolled up)
    if status is not None:
        if status not in STATUSES:
            raise ValueError('invalid status')
        if row['kind'] == 'REQUIREMENT':
            # ignore silently (could also error)
            pass
        else:
            fields.append('status=?'); params.append(status)
    # Allow override only for REQUIREMENT or NFR
    if clear_override:
        fields.append('override_status=NULL')
    elif override_status is not None:
        if override_status not in STATUSES:
            raise ValueError('invalid status')
        if row['kind'] == 'AC':  # allow override for AC? Keep previous rule: disallow
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

def rename_spec(old_id: str, new_id: str):
    if not new_id or new_id == old_id:
        return load_spec(old_id)
    if query_one("SELECT id FROM spec_item WHERE id=?", (new_id,)):
        raise ValueError('target id already exists')
    row = query_one("SELECT * FROM spec_item WHERE id=?", (old_id,))
    if not row:
        return None
    with _lock:
        cur = get_connection().cursor()
        try:
            cur.execute("BEGIN")
            # Insert new copy
            cols = [d[1] for d in cur.execute("PRAGMA table_info(spec_item)")]  # column names
            # Build insert excluding primary key id which we replace
            data = dict(row)
            data['id'] = new_id
            data['updated_at'] = now_iso()
            placeholders = ','.join('?' for _ in cols)
            cur.execute(f"INSERT INTO spec_item ({','.join(cols)}) VALUES ({placeholders})", [data[c] for c in cols])
            # Update children parent refs
            cur.execute("UPDATE spec_item SET parent_id=? WHERE parent_id=?", (new_id, old_id))
            # Update events
            cur.execute("UPDATE verification_event SET spec_id=? WHERE spec_id=?", (new_id, old_id))
            # Delete old row
            cur.execute("DELETE FROM spec_item WHERE id=?", (old_id,))
            cur.execute("COMMIT")
        except Exception:
            try: cur.execute("ROLLBACK")
            except Exception: pass
            raise
    return load_spec(new_id)

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

# Creation helpers ---------------------------------------------------------

def create_feature(feature_key: str, name: str) -> dict:
    """Create a new feature if it doesn't exist."""
    existing = query_one("SELECT feature_key FROM feature WHERE feature_key=?", (feature_key,))
    if existing:
        return {"error": "Feature already exists", "feature_key": feature_key}
    
    execute(
        "INSERT INTO feature (feature_key,name,status,updated_at) VALUES (?,?,?,?)", 
        (feature_key, name, 'UNTESTED', now_iso())
    )
    return dict(load_feature(feature_key))

def create_spec(spec_id: str, feature_key: str, kind: str, description: str, parent_id: Optional[str] = None) -> dict:
    """Create a new spec item."""
    # Validate inputs
    if kind not in ("REQUIREMENT", "AC", "NFR"):
        return {"error": "kind must be REQUIREMENT, AC, or NFR"}
    
    if query_one("SELECT id FROM spec_item WHERE id=?", (spec_id,)):
        return {"error": "Spec already exists", "spec_id": spec_id}
    
    if not query_one("SELECT feature_key FROM feature WHERE feature_key=?", (feature_key,)):
        return {"error": "Feature not found", "feature_key": feature_key}
    
    if parent_id and not query_one("SELECT id FROM spec_item WHERE id=?", (parent_id,)):
        return {"error": "Parent spec not found", "parent_id": parent_id}
    
    execute(
        "INSERT INTO spec_item (id,feature_key,kind,description,parent_id,status,updated_at) VALUES (?,?,?,?,?,?,?)",
        (spec_id, feature_key, kind, description, parent_id, 'UNTESTED', now_iso())
    )
    return dict(load_spec(spec_id))

# MCP-specific helpers ------------------------------------------------------

def get_spec(spec_id: str) -> dict:
    """MCP resource helper - return spec as dict."""
    row = load_spec(spec_id)
    return dict(row) if row else {}

def get_feature(feature_key: str) -> dict:
    """MCP resource helper - return feature as dict."""
    row = load_feature(feature_key)
    return dict(row) if row else {}

def search_specs(status: Optional[str]=None, kind: Optional[str]=None, feature: Optional[str]=None) -> list[dict]:
    """MCP tool helper - search specs with filters."""
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
    rows = query(f"SELECT id, feature_key, kind, description, status, override_status, updated_at FROM spec_item {where} ORDER BY id LIMIT 500", params)
    return [dict(r) for r in rows]

def record_event(spec_id: str, outcome: str, source: str = "", notes: str = "", occurred_at: Optional[str]=None):
    """MCP tool helper - record verification event."""
    ev = {"spec_id": spec_id, "outcome": outcome, "source": source or None, "notes": notes or None}
    if occurred_at:
        ev["occurred_at"] = occurred_at
    return insert_events([ev])

def update_spec_fields(spec_id: str, fields: dict) -> dict:
    """MCP tool helper - update spec fields."""
    patch_args = {k: fields[k] for k in ["description","priority","owner","tags","override_status"] if k in fields}
    updated = patch_spec(spec_id, **patch_args)
    return dict(updated) if updated else {}

ensure_schema(reset=os.environ.get('SPEC_MCP_RESET','0')=='1')
