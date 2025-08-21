"""Typer CLI commands."""
from __future__ import annotations
import typer
from pathlib import Path
import uvicorn
from . import db

from .dashboard import dashboard_app
from .queries import feature_rows
from .verification import record_verification

cli = typer.Typer()

@cli.command()
def dev():
    """Run MCP server (FastMCP) - redirects to the main server."""
    from .mcp_main import main as mcp_main
    mcp_main()

@cli.command()
def db_path():
    """Print the path to the specs.db in use."""
    from . import db as _db
    typer.echo(_db.DB_PATH)

@cli.command()
def dump():
    """Print a JSON-like listing of all feature rows (quick debug)."""
    for r in feature_rows():
        print(dict(r))

@cli.command()
def reset_db():
    """Drop and recreate schema (destructive)."""
    db.ensure_schema(reset=True)
    print("Schema reset.")

@cli.command()
def create_feature(feature_key: str, name: str):
    """Create a new feature if it does not already exist."""
    if db.query_one("SELECT feature_key FROM feature WHERE feature_key=?", (feature_key,)):
        typer.echo("Feature already exists; skipping")
        raise typer.Exit(code=0)
    db.execute("INSERT INTO feature (feature_key,name,status,updated_at) VALUES (?,?,?,?)", (feature_key, name, 'UNTESTED', db.now_iso()))
    typer.echo(f"Created feature {feature_key}")

@cli.command()
def record_event(spec_id: str, outcome: str, source: str|None=None, notes: str|None=None):
    """Record a single verification event (PASSED/FAILED) for a spec item."""
    res = record_verification(spec_id, outcome, source=source, notes=notes)
    print(res)

@cli.command()
def create_spec(
    spec_id: str,
    feature_key: str,
    kind: str = typer.Argument(..., help="REQUIREMENT | AC | NFR"),
    description: str = typer.Option(..., "--description", prompt=True, help="Spec description"),
    parent_id: str | None = typer.Option(None, help="Parent requirement id (for AC/NFR if hierarchical)"),
):
    """Create a spec item manually."""
    kindu = kind.upper()
    if kindu not in ("REQUIREMENT","AC","NFR"):
        raise typer.BadParameter("kind must be REQUIREMENT, AC, or NFR")
    if db.query_one("SELECT id FROM spec_item WHERE id=?", (spec_id,)):
        typer.echo("Spec already exists; aborting")
        raise typer.Exit(code=1)
    if not db.query_one("SELECT feature_key FROM feature WHERE feature_key=?", (feature_key,)):
        raise typer.BadParameter("feature_key not found; create feature first")
    db.execute(
        "INSERT INTO spec_item (id,feature_key,kind,description,parent_id,status,updated_at) VALUES (?,?,?,?,?,?,?)",
        (spec_id, feature_key, kindu, description, parent_id, 'UNTESTED', db.now_iso())
    )
    typer.echo(f"Created spec {spec_id} ({kindu}) for feature {feature_key}")

@cli.command()
def dashboard(host: str = '127.0.0.1', port: int = 8765):
    """Run HTML dashboard web server."""
    uvicorn.run(dashboard_app, host=host, port=port, log_level="info")

def main():  # entrypoint convenience
    cli()
