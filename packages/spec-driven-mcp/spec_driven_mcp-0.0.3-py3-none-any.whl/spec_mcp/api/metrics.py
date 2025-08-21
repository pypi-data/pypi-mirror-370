from __future__ import annotations
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from .. import db

def _counts():
    feature_count = db.query_one("SELECT COUNT(*) c FROM feature")['c']
    kinds = db.query("SELECT kind, COUNT(*) c FROM spec_item GROUP BY kind")
    kind_counts = {r['kind']: r['c'] for r in kinds}
    status_rows = db.query("SELECT status, COUNT(*) c FROM spec_item GROUP BY status")
    status_counts = {r['status']: r['c'] for r in status_rows}
    return {
        'features': feature_count,
        'requirements': kind_counts.get('REQUIREMENT', 0),
        'acceptance_criteria': kind_counts.get('AC', 0),
        'nfr': kind_counts.get('NFR', 0),
        'status_counts': status_counts,
    }

async def summary(request: Request):
    return JSONResponse(_counts())

async def status_distribution(request: Request):
    # status by kind matrix
    rows = db.query("SELECT kind, status, COUNT(*) c FROM spec_item GROUP BY kind, status")
    matrix = {}
    for r in rows:
        matrix.setdefault(r['kind'], {})[r['status']] = r['c']
    return JSONResponse({'by_kind': matrix})

async def events_trend(request: Request):
    days_param = request.query_params.get('days')
    try:
        days = int(days_param) if days_param else 30
    except ValueError:
        days = 30
    # group events by date (UTC date component of occurred_at) limited to range
    # occurred_at stored as ISO; take first 10 chars
    rows = db.query("""
        SELECT substr(occurred_at,1,10) as day,
               SUM(CASE WHEN outcome='PASSED' THEN 1 ELSE 0 END) passed,
               SUM(CASE WHEN outcome='FAILED' THEN 1 ELSE 0 END) failed
        FROM verification_event
        WHERE occurred_at >= date('now','-%d day')
        GROUP BY day
        ORDER BY day ASC
    """ % days)
    # Fill missing days for continuity
    from datetime import date, timedelta
    today = date.today()
    start = today - timedelta(days=days)
    by_day = {r['day']: {'day': r['day'], 'passed': r['passed'], 'failed': r['failed']} for r in rows}
    series = []
    cur = start
    while cur <= today:
        key = cur.isoformat()
        series.append(by_day.get(key, {'day': key, 'passed': 0, 'failed': 0}))
        cur += timedelta(days=1)
    return JSONResponse({'days': days, 'series': series})

async def top_failing(request: Request):
    limit_param = request.query_params.get('limit')
    try:
        limit = int(limit_param) if limit_param else 10
    except ValueError:
        limit = 10
    # failing requirements ordered by number of failing leaf children
    rows = db.query("""
        SELECT r.id, r.description, r.status,
               SUM(CASE WHEN c.status='FAILING' THEN 1 ELSE 0 END) as failing_children,
               SUM(CASE WHEN c.status='VERIFIED' THEN 1 ELSE 0 END) as verified_children,
               SUM(CASE WHEN c.status='UNTESTED' THEN 1 ELSE 0 END) as untested_children,
               COUNT(c.id) as total_children
        FROM spec_item r
        LEFT JOIN spec_item c ON c.parent_id = r.id AND c.kind IN ('AC','NFR')
        WHERE r.kind='REQUIREMENT'
        GROUP BY r.id
        HAVING failing_children > 0
        ORDER BY failing_children DESC, total_children DESC
        LIMIT ?
    """, (limit,))
    return JSONResponse({'items': [dict(r) for r in rows]})

routes = [
    Route('/api/metrics/summary', summary, methods=['GET']),
    Route('/api/metrics/status-distribution', status_distribution, methods=['GET']),
    Route('/api/metrics/events-trend', events_trend, methods=['GET']),
    Route('/api/metrics/top-failing', top_failing, methods=['GET']),
]
