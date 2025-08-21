from .mcp_server import mcp
from .db import ensure_schema
import threading
import socket
import time

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
    # Ensure schema
    ensure_schema()
    
    # Start dashboard in background
    start_dashboard_background()
    
    # Run MCP server via stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
