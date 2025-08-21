from __future__ import annotations
"""Import specs from requirements.md files into SQLite.

Usage:
  python -m spec_mcp.import_specs --spec-root "../p5-bolt/.github/specs"

Behavior:
  - Each feature gets id FEAT-<FeatureKey> (stable) unless exists.
  - Requirements keep their spec IDs (e.g., R-ES-01).
  - Acceptance criteria keep their IDs (AC-ES-001).
  - Status emojis mapped to internal status enumeration.
  - Existing rows are left untouched (idempotent import).
"""
import argparse, re, sys, math
from pathlib import Path
from datetime import datetime
from . import db

EMOJI_MAP = { # used only if we choose to seed synthetic events later (currently unused)
    '�': 'PASSED',
    '🔴': 'FAILED',
}

REQ_RE = re.compile(r"^\[(?P<emoji>[🟢🔵🟡🔴⚪])\s+(?P<id>R-[A-Z0-]+-[0-9]{2,3})]\s+(?P<text>.+)")
AC_RE  = re.compile(r"^\[(?P<emoji>[🟢🔵🟡🔴⚪])\s+(?P<id>AC-[A-Z0-]+-[0-9]{3})]\s+(?P<text>.+)")
NFR_RE = re.compile(r"^\[(?P<emoji>[🟢🔵🟡🔴⚪])\s+(?P<id>NFR-[A-Z0-]+-[0-9]{2,3})]\s+(?P<text>.+)")
FEATURE_KEY_RE = re.compile(r"^Feature Key:\s*(?P<key>[A-Z0-]+)")

def map_status(emoji: str) -> str:
    return EMOJI_MAP.get(emoji, 'UNTESTED')

def infer_category(name: str) -> str:
    n = name.lower()
    if any(k in n for k in ["auth","login","user","account"]):
        return "auth"
    if any(k in n for k in ["editor","preview","sandbox","code"]):
        return "editor"
    if any(k in n for k in ["gallery","upload","asset","media"]):
        return "content"
    if any(k in n for k in ["gcode","vpype","pipeline","plot"]):
        return "pipeline"
    if any(k in n for k in ["ui","navigation","layout","theme"]):
        return "ui"
    return "misc"

def upsert_feature(feature_key: str, name: str, doc_path: str):
    existing = db.query_one("SELECT feature_key FROM feature WHERE feature_key=?", (feature_key,))
    if existing:
        return
    db.execute("INSERT INTO feature (feature_key,name,doc_path,status,updated_at) VALUES (?,?,?,?,?)", (feature_key, name, doc_path, 'UNTESTED', datetime.utcnow().isoformat()+'Z'))

def upsert_spec_item(item_id: str, feature_key: str, kind: str, statement: str, parent_id: str|None):
    if db.query_one("SELECT id FROM spec_item WHERE id=?", (item_id,)):
        return
    title = statement.split('.')[0][:140].strip()
    db.execute("INSERT INTO spec_item (id,feature_key,kind,title,statement,parent_id,status,updated_at) VALUES (?,?,?,?,?,?,?,?)",
               (item_id, feature_key, kind, title, statement, parent_id, 'UNTESTED', datetime.utcnow().isoformat()+'Z'))

def parse_file(path: Path, remap: bool=False):
    content = path.read_text(encoding='utf-8').splitlines()
    feature_key = None
    feature_name = path.parent.name.replace('-', ' ').title()
    section = None
    reqs: list[dict] = []
    acs: list[dict] = []
    nfrs: list[dict] = []
    for line in content:
        mkey = FEATURE_KEY_RE.search(line)
        if mkey:
            feature_key = mkey.group('key')
        if line.strip() == '## Requirements':
            section = 'req'; continue
        if line.strip().startswith('## Acceptance criteria'):
            section = 'ac'; continue
        if line.strip().startswith('## Non') or 'Non‑functional' in line:
            section = 'nfr'; continue
        if line.startswith('## '):
            section = None; continue
        if section == 'req':
            m = REQ_RE.match(line.strip())
            if m: reqs.append(m.groupdict())
        elif section == 'ac':
            m = AC_RE.match(line.strip())
            if m: acs.append(m.groupdict())
        elif section == 'nfr':
            m = NFR_RE.match(line.strip())
            if m: nfrs.append(m.groupdict())
    if not feature_key:
        feature_key = path.parent.name[:4].upper()
    upsert_feature(feature_key, feature_name, str(path))
    # Insert requirements first
    for r in reqs:
        upsert_spec_item(r['id'], feature_key, 'REQUIREMENT', r['text'], None)
    # Map AC to requirement using token similarity
    req_rows = db.query("SELECT id, statement FROM spec_item WHERE feature_key=? AND kind='REQUIREMENT'", (feature_key,))
    def best_req(text: str) -> str|None:
        tokens = _tokenize(text)
        best=None; score=0.0
        for rr in req_rows:
            rtok=_tokenize(rr['statement'])
            if not rtok: continue
            inter=len(tokens & rtok)
            if inter==0: continue
            sc= inter/len(tokens|rtok)
            if sc>score:
                score=sc; best=rr['id']
        return best
    for ac in acs:
        parent=best_req(ac['text']) or (req_rows[0]['id'] if req_rows else None)
        upsert_spec_item(ac['id'], feature_key, 'AC', ac['text'], parent)
    for nf in nfrs:
        parent=best_req(nf['text'])  # may be None (top-level NFR)
        upsert_spec_item(nf['id'], feature_key, 'NFR', nf['text'], parent)

def import_specs(root: Path, remap: bool=False):
    files = [f for f in root.rglob('requirements.md') if '_template' not in f.name]
    for f in files:
        parse_file(f, remap=remap)
    # After import recompute roll-ups
    db.recompute_all()
    return len(files)

STOP_WORDS = {"the","a","an","and","or","to","of","in","on","for","with","shall","when","user","system","that","be","is","are","within"}

def _tokenize(text: str) -> set[str]:
    return {w for w in re.split(r"[^a-z0-9]+", text.lower()) if w and w not in STOP_WORDS and not w.isdigit()}

def _best_requirement(feature_id: str, ac_text: str, req_rows: list[dict]) -> str|None:
    """Choose a requirement whose text best matches the AC text using simple token overlap.
    Returns requirement id or None.
    """
    ac_tokens = _tokenize(ac_text)
    if not ac_tokens:
        return None
    best_id = None
    best_score = 0.0
    for rr in req_rows:
        r_tokens = _tokenize(rr['description']) | _tokenize(rr['title'])
        if not r_tokens:
            continue
        overlap = len(ac_tokens & r_tokens)
        if overlap == 0:
            continue
        # Jaccard similarity
        score = overlap / len(ac_tokens | r_tokens)
        if score > best_score:
            best_score = score
            best_id = rr['id']
    # Require minimal similarity
    if best_score >= 0.05:  # arbitrarily low threshold to allow loose matches
        return best_id
    return None


def import_specs(root: Path, remap: bool=False):
    files = [f for f in root.rglob('requirements.md') if '_template' not in f.name]
    for f in files:
        parse_file(f, remap=remap)
    return len(files)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--spec-root', required=True, help='Path to specs root (.github/specs)')
    parser.add_argument('--remap', action='store_true', help='Re-evaluate and remap existing acceptance criteria to best matching requirement')
    args = parser.parse_args()
    root = Path(args.spec_root).resolve()
    if not root.exists():
        print('Spec root not found', root, file=sys.stderr); sys.exit(1)
    count = import_specs(root, remap=args.remap)
    feats = db.query("SELECT COUNT(*) AS c FROM features")
    reqs = db.query("SELECT COUNT(*) AS c FROM requirements")
    crits = db.query("SELECT COUNT(*) AS c FROM criteria")
    print(f"Imported {count} files. Features={feats[0]['c']} Requirements={reqs[0]['c']} Criteria={crits[0]['c']}")

if __name__ == '__main__':
    main()
