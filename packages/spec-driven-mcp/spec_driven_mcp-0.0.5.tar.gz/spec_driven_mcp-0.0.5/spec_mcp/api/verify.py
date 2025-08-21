from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route
from ..verification import record_verification
from .. import db

async def single_verify(request: Request):
    body = await request.json()
    res = record_verification(body.get('spec_id'), body.get('outcome'), source=body.get('source'), notes=body.get('notes'))
    status = 200 if 'error' not in res else 422
    return JSONResponse(res, status_code=status)

async def batch_verify(request: Request):
    body = await request.json()
    events = body if isinstance(body, list) else body.get('events', [])
    result = db.insert_events(events)
    return JSONResponse(result)

routes = [
    Route('/api/verify', single_verify, methods=['POST']),
    Route('/api/batch-verify', batch_verify, methods=['POST']),
]
