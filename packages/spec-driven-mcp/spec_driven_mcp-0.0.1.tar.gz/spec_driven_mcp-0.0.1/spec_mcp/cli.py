"""Typer CLI commands."""
from __future__ import annotations
import typer
from pathlib import Path
import uvicorn
from . import db
from .app import app
from .dashboard import dashboard_app
from .queries import feature_rows
from .verification import record_verification

cli = typer.Typer()

@cli.command()
def dev():
    """Run MCP server (FastMCP)."""
    app.run()

@cli.command()
def dump():
    for r in feature_rows():
        print(dict(r))

@cli.command()
def reset_db():
    """Drop and recreate schema (destructive)."""
    db.ensure_schema(reset=True)
    print("Schema reset.")

@cli.command()
def import_specs(spec_root: str):
    """Import markdown specs into DB and recompute statuses."""
    from . import import_specs as importer
    count = importer.import_specs(Path(spec_root))
    print(f"Imported {count} spec files.")

@cli.command()
def record_event(spec_id: str, outcome: str, source: str|None=None, notes: str|None=None):
    res = record_verification(spec_id, outcome, source=source, notes=notes)
    print(res)

@cli.command()
def compare(spec_root: str = '../p5-bolt/.github/specs', pretty: bool = True):
    """Compare DB vs markdown specs; exit 2 if mismatch."""
    from .compare_specs import compare as run_compare
    import json, pathlib
    report = run_compare(pathlib.Path(spec_root))
    print(json.dumps(report, indent=2 if pretty else None, default=list))
    if not report['match']:
        raise SystemExit(2)

@cli.command()
def dashboard(host: str = '127.0.0.1', port: int = 8765):
    """Run HTML dashboard web server."""
    uvicorn.run(dashboard_app, host=host, port=port, log_level="info")

def main():  # entrypoint convenience
    cli()
