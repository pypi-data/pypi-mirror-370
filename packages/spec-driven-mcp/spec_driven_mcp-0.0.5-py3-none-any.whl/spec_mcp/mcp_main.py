from .mcp_server import mcp
from .db import ensure_schema, DB_PATH
import threading
import socket
import time
import sys
import argparse
import os
import json

def is_port_available(host: str, port: int) -> bool:
    """Check if a port is available for binding."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0  # Port is available if connection fails
    except Exception:
        return False

def start_dashboard_background():
    """Start the dashboard in the background if it's not already running."""
    host = "127.0.0.1"
    port = 8765
    
    # Check if dashboard is already running
    if not is_port_available(host, port):
        print(f"Dashboard already running at http://{host}:{port}", file=sys.stderr)
        return
    
    try:
        # Import and start dashboard in background thread
        from .dashboard import dashboard_app
        import uvicorn
        
        def run_dashboard():
            # Run with minimal logging to avoid cluttering MCP output
            uvicorn.run(
                dashboard_app,
                host=host,
                port=port,
                log_level="warning",  # Reduce log noise
                access_log=False      # Disable access logs
            )
        
        # Start dashboard in daemon thread (will exit when main process exits)
        dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        dashboard_thread.start()
        
        # Give the dashboard a moment to start
        time.sleep(1)
        
        # Verify it started
        if not is_port_available(host, port):
            print(f"[SUCCESS] Dashboard started at http://{host}:{port}", file=sys.stderr)
        else:
            print("[WARNING] Dashboard may not have started properly", file=sys.stderr)
            
    except Exception as e:
        print(f"[WARNING] Could not start dashboard: {e}", file=sys.stderr)
        print(f"[WARNING] Could not start dashboard: {e}", file=sys.stderr)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        prog="spec-mcp-stdio",
        description="MCP server for specification-driven development",
        epilog="""
This command starts an MCP (Model Context Protocol) server that communicates via JSON-RPC over stdio.
It's designed to be used with VS Code and AI agents like GitHub Copilot.

The server automatically:
- Creates a project-local database at <workspace>/.spec-mcp/specs.db
- Starts a web dashboard at http://localhost:8765
- Provides MCP tools for managing specs and features

For CLI operations, use 'spec-mcp-cli' instead of this command.

Database Location (in priority order):
1. --db-path argument (explicit database file)
2. SPEC_MCP_DB_PATH environment variable
3. Project-local: <workspace>/.spec-mcp/specs.db
4. User data directory (fallback)

Example VS Code MCP configuration (.vscode/mcp.json):
{
  "servers": {
    "specs-mcp": {
      "type": "stdio", 
      "command": "spec-mcp-stdio",
      "args": ["--db-path", "/path/to/custom/specs.db"]
    }
  }
}
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--db-path", 
        help="Explicit database file path (overrides all other location logic)"
    )
    
    # Parse known args (ignore unknown ones for MCP compatibility)
    args, unknown = parser.parse_known_args()
    
    # If --help is provided, show help and exit
    if "--help" in sys.argv or "-h" in sys.argv:
        parser.print_help()
        sys.exit(0)
    
    # Set environment variable from command line argument
    if args.db_path:
        os.environ["SPEC_MCP_DB_PATH"] = args.db_path
    
    # Log workspace and database information for debugging
    print(f"[INFO] MCP Server PID: {os.getpid()}", file=sys.stderr)
    
    # Show database path determination
    if args.db_path:
        print(f"[INFO] Database path from --db-path argument: {args.db_path}", file=sys.stderr)
    elif os.getenv("SPEC_MCP_DB_PATH"):
        print(f"[INFO] Database path from SPEC_MCP_DB_PATH: {os.getenv('SPEC_MCP_DB_PATH')}", file=sys.stderr)
    
    # Show workspace context
    workspace_folders = os.getenv("VSCODE_WORKSPACE_FOLDERS")
    if workspace_folders:
        try:
            folders = json.loads(workspace_folders)
            if folders:
                print(f"[INFO] VS Code workspace folders: {[f.get('uri', '') for f in folders]}", file=sys.stderr)
            else:
                print("[INFO] No VS Code workspace folders found", file=sys.stderr)
        except (json.JSONDecodeError, AttributeError):
            print(f"[INFO] Invalid VSCODE_WORKSPACE_FOLDERS: {workspace_folders}", file=sys.stderr)
    elif os.getenv("SPEC_MCP_WORKSPACE_ROOT"):
        print(f"[INFO] Workspace root from SPEC_MCP_WORKSPACE_ROOT: {os.getenv('SPEC_MCP_WORKSPACE_ROOT')}", file=sys.stderr)
    else:
        print(f"[INFO] No workspace context available, will use fallback", file=sys.stderr)
    
    # Ensure schema and log final database path
    ensure_schema()
    print(f"[INFO] Using database: {DB_PATH}", file=sys.stderr)
    
    # Start dashboard in background
    start_dashboard_background()
    
    # Run MCP server via stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
