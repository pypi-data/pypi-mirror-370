"""MCP server exposing spec & feature resources and mutation tools."""
from __future__ import annotations
from typing import Optional, Literal
from mcp.server.fastmcp import FastMCP
from . import db

mcp = FastMCP("specs-mcp")

# Resources ----------------------------------------------------------------

@mcp.resource("dashboard://status")
def dashboard_resource() -> str:
    """Get dashboard status and URL information."""
    status = dashboard_status()
    if status["status"] == "running":
        return f"[SUCCESS] Dashboard is running at {status['url']}\n\nUse the dashboard to view and manage features and specs."
    else:
        return f"[ERROR] Dashboard not running. {status['message']}\n\nThe dashboard should start automatically with the MCP server."

@mcp.tool()
def search_specs(status: Optional[str] = None, kind: Optional[str] = None, feature: Optional[str]=None) -> list[dict]:
    """Search specs (returns at most 500 items).

    Provide any combination of status, kind (REQUIREMENT|AC|NFR) and feature key.
    """
    return db.search_specs(status=status, kind=kind, feature=feature)

# Tools --------------------------------------------------------------------

@mcp.tool()
def dashboard_status() -> dict:
    """Check if the web dashboard is running and get its URL."""
    import socket
    
    # Check if dashboard is running on default port
    port = 8765
    host = "127.0.0.1"
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return {
                "status": "running",
                "url": f"http://{host}:{port}",
                "message": f"[SUCCESS] Dashboard is running at http://{host}:{port}"
            }
        else:
            return {
                "status": "stopped",
                "url": None,
                "message": "[ERROR] Dashboard is not running. It should start automatically with the MCP server."
            }
    except Exception as e:
        return {
            "status": "unknown", 
            "url": None,
            "message": f"[WARNING] Could not check dashboard status: {e}"
        }

@mcp.tool()
def record_verification(spec_id: str, outcome: Literal["PASSED","FAILED"], source: str = "", notes: str = "", occurred_at: Optional[str]=None) -> dict:
    """Record a verification event for a spec item and return insertion summary."""
    return db.record_event(spec_id=spec_id, outcome=outcome, source=source, notes=notes, occurred_at=occurred_at)

@mcp.tool()
def update_spec(
    spec_id: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    owner: Optional[str] = None,
    tags: Optional[str] = None,
    override_status: Optional[str] = None,
) -> dict:
    """Update mutable fields of a spec item and return the new row."""
    fields = {k: v for k, v in locals().items() if k not in {"spec_id"} and v is not None}
    return db.update_spec_fields(spec_id, fields)

@mcp.tool()
def create_feature(feature_key: str, name: str) -> dict:
    """Create a new feature if it doesn't already exist."""
    return db.create_feature(feature_key, name)

@mcp.tool()
def create_spec(
    spec_id: str,
    feature_key: str,
    kind: Literal["REQUIREMENT", "AC", "NFR"],
    description: str,
    parent_id: Optional[str] = None,
) -> dict:
    """Create a new spec item (requirement, acceptance criterion, or non-functional requirement)."""
    return db.create_spec(spec_id, feature_key, kind, description, parent_id)

@mcp.tool()
def start_dashboard(host: str = "127.0.0.1", port: int = 8765) -> dict:
    """Start the web dashboard server (note: this will block the MCP server)."""
    return {
        "status": "info",
        "message": f"⚠️ Use the CLI to start dashboard: spec-mcp dashboard --host {host} --port {port}",
        "url": f"http://{host}:{port}",
        "command": f"spec-mcp dashboard --host {host} --port {port}"
    }
