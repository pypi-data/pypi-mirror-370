from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route
from .. import db
import json

async def create_feature(request: Request):
    try:
        body = await request.json()
        feature_key = body.get('feature_key', '').strip()
        name = body.get('name', '').strip()
        
        if not feature_key or not name:
            return JSONResponse({'error': 'feature_key and name are required'}, status_code=422)
        
        existing = db.query_one("SELECT feature_key FROM feature WHERE feature_key=?", (feature_key,))
        if existing:
            return JSONResponse({'error': 'Feature already exists'}, status_code=422)
        
        db.execute(
            "INSERT INTO feature (feature_key,name,status,updated_at) VALUES (?,?,?,?)", 
            (feature_key, name, 'UNTESTED', db.now_iso())
        )
        
        feat = db.load_feature(feature_key)
        return JSONResponse(dict(feat))
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)

async def list_features(request: Request):
    rows = db.query("""SELECT feature_key,name,status,override_status FROM feature ORDER BY name""")
    out=[]
    for r in rows:
        counts = db.query("SELECT status, COUNT(*) c FROM spec_item WHERE feature_key=? GROUP BY status", (r['feature_key'],))
        count_map = {c['status']: c['c'] for c in counts}
        out.append({
            'feature_key': r['feature_key'],
            'name': r['name'],
            'status': r['status'],
            'override_status': r['override_status'],
            'counts': count_map,
        })
    return JSONResponse(out)

async def get_feature(request: Request):
    key = request.path_params['feature_key']
    feat = db.load_feature(key)
    if not feat:
        return JSONResponse({'error':'not found'}, status_code=404)
    reqs = db.query("SELECT id,description,status,override_status FROM spec_item WHERE feature_key=? AND kind='REQUIREMENT' ORDER BY id", (key,))
    nfrs = db.query("SELECT id,description,status,override_status FROM spec_item WHERE feature_key=? AND kind='NFR' AND parent_id IS NULL", (key,))
    return JSONResponse({'feature': dict(feat), 'requirements':[dict(r) for r in reqs], 'nfrs':[dict(n) for n in nfrs]})

async def feature_tree(request: Request):
    key = request.path_params['feature_key']
    feat = db.load_feature(key)
    if not feat:
        return JSONResponse({'error':'not found'}, status_code=404)
    # Requirements
    reqs = db.query("SELECT id,description,status,override_status FROM spec_item WHERE feature_key=? AND kind='REQUIREMENT' ORDER BY id", (key,))
    req_list = []
    for r in reqs:
        leaves = db.query("SELECT id,kind,description,status,override_status,parent_id FROM spec_item WHERE parent_id=? ORDER BY id", (r['id'],))
        req_list.append({
            'id': r['id'],
            'description': r['description'],
            'status': r['status'],
            'override_status': r['override_status'],
            'children': [dict(l) for l in leaves]
        })
    top_nfrs = db.query("SELECT id,description,status,override_status FROM spec_item WHERE feature_key=? AND kind='NFR' AND parent_id IS NULL ORDER BY id", (key,))
    return JSONResponse({'feature': dict(feat), 'requirements': req_list, 'top_level_nfrs': [dict(n) for n in top_nfrs]})

async def patch_feature(request: Request):
    key = request.path_params['feature_key']
    body = await request.json()
    try:
        row = db.patch_feature(key, name=body.get('name'), override_status=body.get('override_status'), clear_override=body.get('clear_override', False))
    except ValueError as e:
        return JSONResponse({'error': str(e)}, status_code=422)
    if not row:
        return JSONResponse({'error':'not found'}, status_code=404)
    return JSONResponse(dict(row))

routes = [
    Route('/api/features', list_features, methods=['GET']),
    Route('/api/features', create_feature, methods=['POST']),
    Route('/api/features/{feature_key}', get_feature, methods=['GET']),
    Route('/api/features/{feature_key}/tree', feature_tree, methods=['GET']),
    Route('/api/features/{feature_key}', patch_feature, methods=['PATCH']),
]
