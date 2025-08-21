"""MCP FastMCP app and tools registration."""
from __future__ import annotations
from typing import Optional, Literal
import threading
import uvicorn
import logging
from mcp.server.fastmcp import FastMCP
from . import db
from .verification import record_verification as _record_verification_impl

app = FastMCP("spec-driven-mcp")

# Global variable to track dashboard status
_dashboard_thread = None
_dashboard_running = False

def start_dashboard_background(host: str = "127.0.0.1", port: int = 8765):
    """Start the dashboard in a background thread."""
    global _dashboard_thread, _dashboard_running
    
    if _dashboard_running:
        return {"status": "already_running", "url": f"http://{host}:{port}"}
    
    from .dashboard import dashboard_app
    
    def run_dashboard():
        global _dashboard_running
        try:
            # Suppress uvicorn access logs to avoid cluttering MCP server output
            uvicorn_logger = logging.getLogger("uvicorn.access")
            uvicorn_logger.setLevel(logging.WARNING)
            
            _dashboard_running = True
            # Give a small delay to let MCP server initialize first
            import time
            time.sleep(0.5)
            
            uvicorn.run(dashboard_app, host=host, port=port, log_level="error")
        except Exception as e:
            _dashboard_running = False
            # Silently fail for auto-start, don't clutter MCP output
            pass
    
    _dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    _dashboard_thread.start()
    
    return {"status": "started", "url": f"http://{host}:{port}"}

# Auto-start dashboard when MCP server initializes
import atexit
def cleanup_dashboard():
    global _dashboard_running
    _dashboard_running = False

atexit.register(cleanup_dashboard)

# Start dashboard after a short delay to let MCP server initialize
def delayed_dashboard_start():
    import time
    time.sleep(1.0)  # Wait for MCP server to be ready
    start_dashboard_background()

threading.Thread(target=delayed_dashboard_start, daemon=True).start()

# Tools ----------------------------------------------------------------

@app.tool()
def create_feature(feature_key: str, name: str) -> dict:
    """Create a new feature if it doesn't already exist."""
    existing = db.query_one("SELECT feature_key FROM feature WHERE feature_key=?", (feature_key,))
    if existing:
        return {"error": "Feature already exists", "feature_key": feature_key}
    
    db.execute(
        "INSERT INTO feature (feature_key,name,status,updated_at) VALUES (?,?,?,?)", 
        (feature_key, name, 'UNTESTED', db.now_iso())
    )
    row = db.load_feature(feature_key)
    return dict(row) if row else {}

@app.tool()
def create_spec(spec_id: str, feature_key: str, kind: Literal["REQUIREMENT","AC","NFR"], statement: str, parent_id: Optional[str] = None) -> dict:
    """Create a new spec item (requirement, acceptance criterion, or non-functional requirement)."""
    # Validate inputs
    if kind not in ("REQUIREMENT", "AC", "NFR"):
        return {"error": "kind must be REQUIREMENT, AC, or NFR"}
    
    if db.query_one("SELECT id FROM spec_item WHERE id=?", (spec_id,)):
        return {"error": "Spec already exists", "spec_id": spec_id}
    
    if not db.query_one("SELECT feature_key FROM feature WHERE feature_key=?", (feature_key,)):
        return {"error": "Feature not found", "feature_key": feature_key}
    
    if parent_id and not db.query_one("SELECT id FROM spec_item WHERE id=?", (parent_id,)):
        return {"error": "Parent spec not found", "parent_id": parent_id}
    
    title = statement.split('.')[0][:140].strip()
    db.execute(
        "INSERT INTO spec_item (id,feature_key,kind,title,statement,parent_id,status,updated_at) VALUES (?,?,?,?,?,?,?,?)",
        (spec_id, feature_key, kind, title, statement, parent_id, 'UNTESTED', db.now_iso())
    )
    row = db.load_spec(spec_id)
    return dict(row) if row else {}

@app.tool()
def record_verification(spec_id: str, outcome: Literal["PASSED","FAILED"], source: Optional[str]=None, notes: Optional[str]=None, occurred_at: Optional[str]=None) -> dict:
    """Record a verification event for a spec item and return insertion summary."""
    return _record_verification_impl(spec_id, outcome, source=source, notes=notes, occurred_at=occurred_at)

@app.tool()
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
    if not fields:
        row = db.load_spec(spec_id)
        return dict(row) if row else {}
    
    updated = db.patch_spec(spec_id, **fields)
    return dict(updated) if updated else {}

@app.tool()
def search_specs(status: Optional[str] = None, kind: Optional[str] = None, feature: Optional[str] = None) -> list[dict]:
    """Search specs (returns at most 500 items).

    Provide any combination of status, kind (REQUIREMENT|AC|NFR) and feature key.
    """
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
    rows = db.query(f"SELECT id, feature_key, kind, title, statement, status, override_status, updated_at FROM spec_item {where} ORDER BY id LIMIT 500", params)
    return [dict(r) for r in rows]

@app.tool()
def start_dashboard(host: str = "127.0.0.1", port: int = 8765) -> dict:
    """Start or check status of the HTML dashboard web server."""
    global _dashboard_running
    
    if _dashboard_running:
        return {
            "status": "already_running",
            "url": f"http://{host}:{port}",
            "message": f"Dashboard is already running at http://{host}:{port}"
        }
    
    result = start_dashboard_background(host, port)
    if result["status"] == "started":
        result["message"] = f"Dashboard server started at http://{host}:{port}"
    
    return result

@app.tool()
def dashboard_status() -> dict:
    """Check if the dashboard is running and get its URL."""
    global _dashboard_running
    
    if _dashboard_running:
        return {
            "status": "running",
            "url": "http://127.0.0.1:8765",
            "message": "Dashboard is running at http://127.0.0.1:8765"
        }
    else:
        return {
            "status": "stopped",
            "message": "Dashboard is not running. Use start_dashboard() to start it."
        }

# Resources ------------------------------------------------------------

@app.resource("spec://{spec_id}")
def spec_resource(spec_id: str) -> dict:
    """Return a single spec item (empty dict if not found)."""
    row = db.load_spec(spec_id)
    return dict(row) if row else {}

@app.resource("feature://{feature_key}")
def feature_resource(feature_key: str) -> dict:
    """Return a feature row (empty dict if not found)."""
    row = db.load_feature(feature_key)
    return dict(row) if row else {}
