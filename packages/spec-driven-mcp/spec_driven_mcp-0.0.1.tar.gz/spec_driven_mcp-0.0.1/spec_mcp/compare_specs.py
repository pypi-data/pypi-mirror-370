"""Compare current database contents with a fresh parse of requirements markdown files.

Usage (inside venv):
  python -m spec_mcp.compare_specs --spec-root ../p5-bolt/.github/specs --pretty

Exit codes: 0 = match, 2 = mismatch, 1 = error
"""
from __future__ import annotations
import json, os, pathlib, importlib
from typing import Any, Dict
from . import db as live_db

def collect_live() -> Dict[str, Any]:
    conn = live_db._connect()  # separate connection
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM feature'); feature_count = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM spec_item'); spec_item_count = cur.fetchone()[0]
    cur.execute('SELECT kind, COUNT(*) FROM spec_item GROUP BY kind'); kind_counts = dict(cur.fetchall())
    cur.execute('SELECT feature_key FROM feature'); features = {r[0] for r in cur.fetchall()}
    cur.execute('SELECT id FROM spec_item'); spec_ids = {r[0] for r in cur.fetchall()}
    return {
        'feature_count': feature_count,
        'spec_item_count': spec_item_count,
        'kind_counts': kind_counts,
        'features': features,
        'spec_ids': spec_ids,
    }

def collect_from_files(spec_root: pathlib.Path) -> Dict[str, Any]:
    temp_db_path = spec_root / 'temp_compare.db'
    if temp_db_path.exists():
        temp_db_path.unlink()
    original = os.environ.get('SPEC_MCP_DB')
    os.environ['SPEC_MCP_DB'] = str(temp_db_path)
    from spec_mcp import db as tempdb
    importlib.reload(tempdb)  # type: ignore
    from spec_mcp import import_specs as importer
    parsed_files = importer.import_specs(spec_root)
    conn = tempdb._connect(); cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM feature'); feature_count = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM spec_item'); spec_item_count = cur.fetchone()[0]
    cur.execute('SELECT kind, COUNT(*) FROM spec_item GROUP BY kind'); kind_counts = dict(cur.fetchall())
    cur.execute('SELECT feature_key FROM feature'); features = {r[0] for r in cur.fetchall()}
    cur.execute('SELECT id FROM spec_item'); spec_ids = {r[0] for r in cur.fetchall()}
    # restore env
    if original is not None:
        os.environ['SPEC_MCP_DB'] = original
    else:
        os.environ.pop('SPEC_MCP_DB', None)
    return {
        'db_path': str(temp_db_path),
        'parsed_files': parsed_files,
        'feature_count': feature_count,
        'spec_item_count': spec_item_count,
        'kind_counts': kind_counts,
        'features': features,
        'spec_ids': spec_ids,
    }

def compare(spec_root: pathlib.Path) -> Dict[str, Any]:
    live = collect_live()
    files = collect_from_files(spec_root)
    diff = {
        'features_missing_in_files': sorted(live['features'] - files['features']),
        'features_only_in_files': sorted(files['features'] - live['features']),
        'spec_ids_missing_in_files': sorted(live['spec_ids'] - files['spec_ids']),
        'spec_ids_only_in_files': sorted(files['spec_ids'] - live['spec_ids']),
    }
    match = (not diff['features_missing_in_files'] and not diff['features_only_in_files'] and
             not diff['spec_ids_missing_in_files'] and not diff['spec_ids_only_in_files'] and
             live['feature_count']==files['feature_count'] and
             live['spec_item_count']==files['spec_item_count'] and
             live['kind_counts']==files['kind_counts'])
    return {
        'spec_root': str(spec_root),
        'live_summary': {k: v for k,v in live.items() if k not in ('features','spec_ids')},
        'files_summary': {k: v for k,v in files.items() if k not in ('features','spec_ids')},
        'diff': diff,
        'match': match,
    }

def main(argv: list[str] | None = None):
    import argparse
    p = argparse.ArgumentParser(description='Compare DB vs markdown specs')
    p.add_argument('--spec-root', required=True, help='Path to .github/specs directory')
    p.add_argument('--pretty', action='store_true', help='Pretty-print JSON')
    args = p.parse_args(argv)
    root = pathlib.Path(args.spec_root).resolve()
    if not root.exists():
        print(json.dumps({'error':'spec_root not found','path':str(root)}))
        return 1
    report = compare(root)
    print(json.dumps(report, indent=2 if args.pretty else None, default=list))
    if not report['match']:
        return 2
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
