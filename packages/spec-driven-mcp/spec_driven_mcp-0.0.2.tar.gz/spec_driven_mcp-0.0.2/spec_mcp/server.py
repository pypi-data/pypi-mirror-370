from __future__ import annotations
"""MCP Server entry point with auto-starting dashboard.

This server provides:
 - MCP tools and resources for VS Code integration
 - Auto-starting web dashboard at http://localhost:8765
 - All functionality in a single, focused package
"""

from . import db  # noqa: F401  (side-effect: ensure schema on import)
from .app import app  # noqa: F401

def main():
    """Main entry point - runs MCP server with auto-starting dashboard."""
    app.run(transport="stdio")

if __name__ == "__main__":  # pragma: no cover
    main()
