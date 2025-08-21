from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route
from .. import db

VALID_KINDS = {'REQUIREMENT','AC','NFR'}

async def create_spec(request: Request):
    try:
        body = await request.json()
        spec_id = body.get('spec_id', '').strip()
        feature_key = body.get('feature_key', '').strip()
        kind = body.get('kind', '').strip().upper()
        description = body.get('description', '').strip()
        parent_id = body.get('parent_id')
        
        if not all([spec_id, feature_key, kind, description]):
            return JSONResponse({'error': 'spec_id, feature_key, kind, and description are required'}, status_code=422)
        
        if kind not in VALID_KINDS:
            return JSONResponse({'error': 'kind must be REQUIREMENT, AC, or NFR'}, status_code=422)
        
        if db.query_one("SELECT id FROM spec_item WHERE id=?", (spec_id,)):
            return JSONResponse({'error': 'Spec already exists'}, status_code=422)
        
        if not db.query_one("SELECT feature_key FROM feature WHERE feature_key=?", (feature_key,)):
            return JSONResponse({'error': 'Feature not found'}, status_code=422)
        
        if parent_id and not db.query_one("SELECT id FROM spec_item WHERE id=?", (parent_id,)):
            return JSONResponse({'error': 'Parent spec not found'}, status_code=422)
        
        db.execute(
            "INSERT INTO spec_item (id,feature_key,kind,description,parent_id,status,updated_at) VALUES (?,?,?,?,?,?,?)",
            (spec_id, feature_key, kind, description, parent_id, 'UNTESTED', db.now_iso())
        )
        
        spec = db.load_spec(spec_id)
        return JSONResponse(dict(spec))
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)

async def list_specs(request: Request):
    params = request.query_params
    feature = params.get('feature')
    kind = params.get('kind')
    status = params.get('status')
    q = (params.get('q') or '').lower().strip()
    sql = "SELECT id,feature_key,kind,description,status,override_status,parent_id FROM spec_item WHERE 1=1"
    args = []
    if feature:
        sql += " AND feature_key=?"; args.append(feature)
    if kind and kind in VALID_KINDS:
        sql += " AND kind=?"; args.append(kind)
    if status:
        sql += " AND status=?"; args.append(status)
    rows = db.query(sql + " ORDER BY id LIMIT 500", args)
    out=[]
    for r in rows:
        if q and q not in (r['id'].lower() + (r['description'] or '').lower()):
            continue
        out.append(dict(r))
    return JSONResponse({'items': out, 'count': len(out)})

async def get_spec(request: Request):
    sid = request.path_params['spec_id']
    row = db.load_spec(sid)
    if not row:
        return JSONResponse({'error':'not found'}, status_code=404)
    children=None
    if row['kind']=='REQUIREMENT':
        kids = db.query("SELECT id,kind,description,status,override_status FROM spec_item WHERE parent_id=? ORDER BY id", (sid,))
        children=[dict(k) for k in kids]
    events = db.events_for_spec(sid, limit=50)
    return JSONResponse({'spec': dict(row), 'children': children, 'events':[dict(e) for e in events]})

async def patch_spec(request: Request):
    sid = request.path_params['spec_id']
    body = await request.json()
    try:
        updated = db.patch_spec(sid, description=body.get('description'), override_status=body.get('override_status'), clear_override=body.get('clear_override', False))
    except ValueError as e:
        return JSONResponse({'error': str(e)}, status_code=422)
    if not updated:
        return JSONResponse({'error':'not found'}, status_code=404)
    return JSONResponse(dict(updated))

routes = [
    Route('/api/specs', list_specs, methods=['GET']),
    Route('/api/specs', create_spec, methods=['POST']),
    Route('/api/specs/{spec_id}', get_spec, methods=['GET']),
    Route('/api/specs/{spec_id}', patch_spec, methods=['PATCH']),
]
