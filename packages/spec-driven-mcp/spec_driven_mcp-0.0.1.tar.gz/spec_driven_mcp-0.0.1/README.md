# Spec Driven MCP Server

Authoritative source-of-truth for product & engineering specifications exposed via the Model Context Protocol (MCP), a lightweight HTTP dashboard, and a CLI. Designed to keep markdown specs, live status, and automated verification events in permanent sync.

---
## Current Scope (2025-08)

### Core Entities (SQLite)
| Table | Purpose |
|-------|---------|
| `feature` | High‑level capability (business/UX slice) keyed by `feature_key` (stable slug). |
| `spec_item` | Hierarchical spec nodes. `kind ∈ {REQUIREMENT, AC, NFR}`. REQUIREMENT can have AC (acceptance criteria) and NFR children. Top‑level NFR also allowed (no parent). |
| `verification_event` | Immutable pass/fail evidence (`outcome ∈ {PASSED, FAILED}`) attached to any `spec_item` (usually AC/NFR). |

### Status Model
Canonical computed statuses are restricted to: `UNTESTED`, `FAILING`, `PARTIAL`, `VERIFIED`.

Roll‑up rules:
1. Leaf (AC or NFR without children): status derived from its latest verification event (FAILED → FAILING, PASSED → VERIFIED, none → UNTESTED).
2. REQUIREMENT: roll up its direct leaf children (AC + NFR) plus (optionally) itself if it has direct events (virtual leaf).   
3. FEATURE: roll up all REQUIREMENTs plus any top‑level NFR (kind=NFR & parent_id NULL).
4. Roll‑up algorithm:  
   - Any FAILING → `FAILING`  
   - All VERIFIED → `VERIFIED`  
   - Mixed VERIFIED/UNTESTED (no FAILING) → `PARTIAL`  
   - Otherwise → `UNTESTED`

### Overrides
`feature.override_status` and `spec_item.override_status` allow manual intervention. For AC items overrides are blocked (by design). Effective status used in UI and future reports is `override_status or status`.

### What Changed vs Original MVP
| Aspect | Original Draft | Current Implementation |
|--------|----------------|------------------------|
| Storage | JSON flat files | SQLite (`specs.db`) with transactional updates |
| Entity set | Feature, Requirement, AcceptanceCriterion, TestLink | Feature + unified `spec_item` (REQUIREMENT/AC/NFR) + events (no TestLink table yet) |
| Status vocabulary | idea→released lifecycle | Focused verification states (UNTESTED/FAILING/PARTIAL/VERIFIED) |
| Verification | Implied via test links | Explicit `verification_event` log (PASSED/FAILED) |
| Editing | CLI/tools only | Interactive dashboard (htmx + Alpine.js) + PATCH API |
| MCP tools | CRUD variety (planned) | `record_verification` tool + resource views (read) |

---
## Directory Overview
```
spec_mcp/
  app.py            # FastMCP app and tool registration
  resources.py      # MCP resource handlers (text views)
  db.py             # SQLite schema & status recomputation logic
  verification.py   # Shared record_verification implementation
  queries.py        # Aggregated query helpers (feature/spec rows)
  api/              # Modular Starlette JSON + fragment endpoints
  dashboard.py      # Tailwind/htmx/Alpine dashboard Starlette app
  cli.py            # Typer CLI (entrypoint for all operations)
  server.py         # Slim compatibility entrypoint (re-exports)
  import_specs.py   # Markdown spec importer
  compare_specs.py  # Drift detection (DB vs markdown)
  data/specs.db     # SQLite file (auto-created)
```

---
## Installation
Using `uv` (recommended):
```bash
uv sync
```

Using pip:
```bash
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -e .
```

Environment variables:
| Variable | Purpose | Default |
|----------|---------|---------|
| `SPEC_MCP_DB` | Path to SQLite DB file | `spec_mcp/data/specs.db` |
| `SPEC_MCP_RESET=1` | Force schema drop & recreate at import | off |

---
## CLI
All commands exposed via the installed script `spec-mcp` (or `python -m spec_mcp.server`).

| Command | Description |
|---------|-------------|
| `dev` | Run MCP stdio server (FastMCP). |
| `dashboard` | Launch web dashboard (Starlette + Tailwind). |
| `import-specs <dir>` | Parse markdown requirements and load/update DB. |
| `compare` | Compare DB contents with markdown specs (exit code 2 on drift). |
| `reset-db` | Drop and recreate schema (destructive). |
| `record-event` | Manually append a verification event. |
| `dump` | Output summarized feature rows to stdout. |

Examples:
```bash
spec-mcp import-specs ../p5-bolt/.github/specs
spec-mcp compare --spec-root ../p5-bolt/.github/specs
spec-mcp dashboard --port 8765
spec-mcp record-event SPEC-AC-123 PASSED --source "unit:test::id"
```

---
## Dashboard (HTTP UI)
Features:
* Global search & status filters.
* Feature cards with aggregated counts (verified / failing / untested / partial).
* Feature detail view: requirements, AC, NFR sections.
* Inline editing (htmx swaps) for title, statement, and status overrides (except AC).
* Quick status color chips.

Tech: Starlette routes + Tailwind via CDN + htmx (2.x) + Alpine.js (minimal usage).

Start:
```bash
spec-mcp dashboard --host 127.0.0.1 --port 8765
```

---
## HTTP API (JSON)
Base served from the same Starlette app as the dashboard.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/features` | List features + status counts. |
| GET | `/api/features/{feature_key}` | Feature details (requirements + top-level NFRs). |
| PATCH | `/api/features/{feature_key}` | Update name / override status / clear override. |
| GET | `/api/specs` | Query spec items (filters: feature, kind, status, q). |
| GET | `/api/specs/{spec_id}` | Spec with children (if requirement) + recent events. |
| PATCH | `/api/specs/{spec_id}` | Update title, statement, override status (not AC). |
| POST | `/api/verify` | Record single verification event. Body: `{spec_id,outcome,source?,notes?}`. |
| POST | `/api/batch-verify` | Bulk events: `[{spec_id,outcome,...}, ...]`. |
| GET | `/fragments/spec/{spec_id}` | HTML fragment (read view). |
| GET | `/fragments/spec/{spec_id}/edit` | HTML fragment (edit form). |
| PATCH | `/fragments/spec/{spec_id}` | Update spec via form (htmx). |

Status codes: `404` not found, `422` validation error.

---
## MCP Interface

Two entrypoints are now provided:

### 1. Legacy (in-repo) FastMCP App
Name: `spec-driven-mcp`

Implements a minimal `record_verification` tool (historical). Retained for backward compatibility; **prefer the packaged server below** for richer capabilities.

### 2. Packaged MCP Server (`specs_mcp` package)
Run via stdio:
```bash
python -m specs_mcp
```
or (if using `uv`):
```bash
uv run python -m specs_mcp
```

Environment variable (optional):
| Var | Effect | Default |
|-----|--------|---------|
| `SPEC_MCP_DB` | Path to SQLite DB used by the server | `spec_mcp/data/specs.db` |

Resources (structured URIs):
| URI | Description |
|-----|-------------|
| `spec://{spec_id}` | Single spec item (empty object if not found). |
| `feature://{feature_key}` | Single feature row (empty object if not found). |

Tools (stdio JSON RPC via MCP):
| Tool | Parameters | Purpose |
|------|------------|---------|
| `record_verification` | `spec_id`, `outcome` (PASSED/FAILED), `source?`, `notes?`, `occurred_at?` | Insert a verification event (recomputes hierarchy). |
| `update_spec` | `spec_id`, optional any of: `title`, `statement`, `rationale`, `priority`, `owner`, `tags`, `override_status` | Patch mutable spec fields & return updated row. |
| `search_specs` | Optional filters: `status`, `kind` (REQUIREMENT/AC/NFR), `feature` | Return up to 500 matching spec rows. |

Notes:
* Overrides still disallowed for AC items (tool will error).
* All tools are idempotent aside from `record_verification` which appends history.

### VS Code / GitHub Copilot Chat Integration
Create `.vscode/mcp.json` in the *target* project (not necessarily this repo):
```jsonc
{
  "servers": {
    "specs-mcp": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "specs_mcp"],
      "env": { "SPEC_MCP_DB": "${workspaceFolder}/specs.db" }
    }
  }
}
```
Then in VS Code: *MCP View → Start Server* or use the command palette. Tools & resources become available in Copilot Chat (Agent / Tools mode).

### Using in Other Projects
You can embed or reuse this MCP server to give AI agents structured access to your specification database:
1. **Install** (choose one):
   * Directly from source (monorepo style): add this directory to your project and ensure it is on `PYTHONPATH`.
   * (If published) `pip install spec-driven-mcp` (future).
2. **Provide a DB**: either copy an existing `specs.db` or run the importer against your markdown specs.
3. **Configure** `.vscode/mcp.json` (example above) pointing `SPEC_MCP_DB` to a path inside the consuming project so each repo can maintain its own spec database.
4. **Import Specs** (optional initial load):
   ```bash
   # from the spec-driven-mcp project root
   spec-mcp import-specs /path/to/other-project/.github/specs
   # copy or symlink the resulting specs.db into the other project, OR run importer inside that project if you vend the CLI there too
   ```
5. **Run Server**: `python -m specs_mcp` inside the other project workspace (VS Code will do this automatically once configured).
6. **Consume Tools**: In Copilot Chat ask e.g.:
   * "List failing acceptance criteria" → the agent can call `search_specs(status="FAILING", kind="AC")`.
   * "Mark AC-LOGIN-002 as passed" → calls `record_verification`.
   * "Update the title of REQ-LOGIN-001" → calls `update_spec`.

### Programmatic Use (Embedding)
```python
from specs_mcp.server import mcp  # FastMCP instance
from specs_mcp import db

db.ensure_schema()  # ensure tables
# Start in-process (blocks):
mcp.run(transport="stdio")
```

For a custom event loop (embedding inside another process) see the official MCP Python SDK docs.

### Roadmap (MCP Layer)
* Feature creation / spec creation tools.
* Bulk import tool.
* Rich diff / drift resolution tool.
* Prompt surfaces for drafting acceptance criteria (e.g. EARS template prompt).

---
## Markdown Import & Drift Detection
Specs in markdown (e.g., `../p5-bolt/.github/specs/**/requirements.md`) are parsed and ingested. Each requirement / acceptance criterion / non‑functional requirement must follow the repository’s standardized bracket notation. After editing markdown, re‑import and run `compare` to ensure DB alignment. Exit code 2 signals drift for CI gating.

Typical loop:
```bash
spec-mcp import-specs ../p5-bolt/.github/specs
spec-mcp compare --spec-root ../p5-bolt/.github/specs
```

---
## Verification Events
Use either HTTP (`POST /api/verify`) or MCP tool (`record_verification`) to push results. CI pipelines and local test adapters can batch insert using `/api/batch-verify` for efficiency.

Event fields: `id` (auto), `spec_id`, `outcome`, `occurred_at` (ISO, supplied or default now UTC), `source` (test harness / human / tool), `notes`.

Propagation is incremental: the touched leaf recomputes, then its parent requirement, then the feature.

---
## Extension Points / Next Steps
1. Test linkage table (explicit mapping to test case IDs + last result snapshot).
2. Additional MCP tools (search, patch, create feature/spec).
3. OpenAPI schema & typed client generation.
4. Auth (API tokens) & audit enrichment.
5. Historical status trend charts (materialized timeline).
6. Gherkin / ReqIF import-export.
7. Multi-repository project aggregation.
8. Structured tagging & priority weighting for roll-up metrics.
9. AI assistant prompts auto-drafting acceptance criteria.
10. Notification hooks (webhook on FAILING transitions).

---
## Development Notes
* Pure Python + SQLite, no migrations framework (schema auto-ensured on import). Backward-compatible additive changes use `ALTER TABLE` in `ensure_schema`.
* Concurrency: simple RLock; adequate for low write volume (CLI/CI). For higher concurrency consider per-connection or WAL tuning.
* AC override prohibition ensures verification truth derives solely from evidence.
* All roll-up logic localized in `db.py` for transparency and testability.

---
## Minimal Programmatic Example
```python
from spec_mcp.verification import record_verification

# Mark an acceptance criterion as passed
resp = record_verification("AC-LOGIN-001", "PASSED", source="pytest::test_login")
print(resp)  # {'id': 'AC-LOGIN-001', 'status': 'VERIFIED'}
```

---
## License
MIT
