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
        print(f"Dashboard already running at http://{host}:{port}")
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
            print(f"[SUCCESS] Dashboard started at http://{host}:{port}")
        else:
            print("[WARNING] Dashboard may not have started properly")
            
    except Exception as e:
        print(f"[WARNING] Could not start dashboard: {e}")

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

For CLI operations, use 'spec-mcp' instead of this command.

Example VS Code MCP configuration (.vscode/mcp.json):
{
  "servers": {
    "specs-mcp": {
      "type": "stdio", 
      "command": "spec-mcp-stdio"
    }
  }
}
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # If --help is provided, show help and exit
    if "--help" in sys.argv or "-h" in sys.argv:
        parser.print_help()
        sys.exit(0)
    
    # Log workspace and database information for debugging
    print(f"[INFO] MCP Server PID: {os.getpid()}")
    workspace_folders = os.getenv("VSCODE_WORKSPACE_FOLDERS")
    if workspace_folders:
        try:
            folders = json.loads(workspace_folders)
            if folders:
                print(f"[INFO] VS Code workspace folders: {[f.get('uri', '') for f in folders]}")
            else:
                print("[INFO] No VS Code workspace folders found")
        except (json.JSONDecodeError, AttributeError):
            print(f"[INFO] Invalid VSCODE_WORKSPACE_FOLDERS: {workspace_folders}")
    else:
        print(f"[INFO] No VS Code workspace detected, using CWD: {os.getcwd()}")
    
    # Ensure schema and log database path
    ensure_schema()
    print(f"[INFO] Using database: {DB_PATH}")
    
    # Start dashboard in background
    start_dashboard_background()
    
    # Run MCP server via stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
