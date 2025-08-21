from __future__ import annotations
"""Slim entrypoint kept for backwards compatibility.

The original monolithic server was decomposed into focused modules:
 - app.py          FastMCP app & tools
 - resources.py    MCP resource handlers
 - verification.py Shared verification logic
 - queries.py      DB query helpers
 - dashboard.py    Starlette dashboard application
 - cli.py          Typer CLI (includes dashboard command)

This file just ensures the DB schema is loaded and re-exports app/cli so
`python -m spec_mcp.server` continues to work.
"""

from . import db  # noqa: F401  (side-effect: ensure schema on import)
from .app import app  # noqa: F401
from .cli import cli, main  # noqa: F401

if __name__ == "__main__":  # pragma: no cover
    main()
