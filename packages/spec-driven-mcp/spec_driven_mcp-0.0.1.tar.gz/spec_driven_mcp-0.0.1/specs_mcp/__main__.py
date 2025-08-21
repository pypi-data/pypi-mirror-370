from .server import mcp
from .db import ensure_schema

if __name__ == "__main__":
    # Ensure schema then run via stdio transport (default, but explicit for clarity)
    ensure_schema()
    mcp.run(transport="stdio")
