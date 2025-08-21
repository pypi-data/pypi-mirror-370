from starlette.responses import HTMLResponse
from starlette.requests import Request
from starlette.routing import Route
from .. import db

# Simple HTML fragments for htmx swaps

def _status_chip(st: str) -> str:
    return f"<span class='px-2 py-0.5 rounded text-xs bg-slate-700'>{st}</span>"

async def spec_view(request: Request):
    sid = request.path_params['spec_id']
    row = db.load_spec(sid)
    if not row:
        return HTMLResponse("<div class='text-rose-400 text-xs'>Not found</div>", status_code=404)
    return HTMLResponse(
        f"<div class='space-y-1' data-spec='{row['id']}'><div class='flex items-center gap-2'><code class='text-sky-400'>{row['id']}</code>{_status_chip(row['status'])}<button hx-get='/fragments/spec/{row['id']}/edit' class='text-xs text-slate-400 hover:text-slate-200 underline ml-auto'>Edit</button></div><div class='text-xs text-slate-400'>{(row['description'] or '')}</div></div>"
    )

async def spec_edit(request: Request):
    sid = request.path_params['spec_id']
    row = db.load_spec(sid)
    if not row:
        return HTMLResponse("<div class='text-rose-400 text-xs'>Not found</div>", status_code=404)
    disable_status = 'disabled' if row['kind']=='AC' else ''
    return HTMLResponse(
        f"<form hx-patch='/fragments/spec/{row['id']}' hx-target='closest [data-spec]' hx-swap='outerHTML' class='space-y-1' data-spec='{row['id']}'>"
        f"<div class='flex items-center gap-2'><code class='text-sky-400'>{row['id']}</code><select name='override_status' class='bg-slate-800 border border-slate-600 rounded text-xs px-1 py-0.5' {disable_status}><option value=''>--status--</option><option {'selected' if row['override_status']=='UNTESTED' else ''}>UNTESTED</option><option {'selected' if row['override_status']=='FAILING' else ''}>FAILING</option><option {'selected' if row['override_status']=='PARTIAL' else ''}>PARTIAL</option><option {'selected' if row['override_status']=='VERIFIED' else ''}>VERIFIED</option></select><button name='clear_override' value='1' class='text-xs text-amber-400'>Clear</button><button type='submit' class='ml-auto text-xs bg-sky-600 hover:bg-sky-500 px-2 py-0.5 rounded'>Save</button></div>"
        f"<textarea name='description' rows='3' class='w-full bg-slate-800 border border-slate-600 rounded px-2 py-1 text-xs' placeholder='Description'>{(row['description'] or '').replace('<','&lt;')}</textarea>"
        f"</form>"
    )

async def spec_patch(request: Request):
    sid = request.path_params['spec_id']
    form = await request.form()
    override_status = form.get('override_status') or None
    clear = bool(form.get('clear_override'))
    if override_status == '--status--':
        override_status = None
    description = form.get('description') or None
    try:
        updated = db.patch_spec(sid, description=description, override_status=override_status, clear_override=clear)
    except ValueError as e:
        return HTMLResponse(f"<div class='text-rose-400 text-xs'>Error: {e}</div>", status_code=422)
    if not updated:
        return HTMLResponse("<div class='text-rose-400 text-xs'>Not found</div>", status_code=404)
    # Return view fragment
    row = updated
    return HTMLResponse(
        f"<div class='space-y-1' data-spec='{row['id']}'><div class='flex items-center gap-2'><code class='text-sky-400'>{row['id']}</code>{_status_chip(row['status'])}<button hx-get='/fragments/spec/{row['id']}/edit' class='text-xs text-slate-400 hover:text-slate-200 underline ml-auto'>Edit</button></div><div class='text-xs text-slate-400'>{(row['description'] or '')}</div></div>"
    )

routes = [
    Route('/fragments/spec/{spec_id}', spec_view, methods=['GET']),
    Route('/fragments/spec/{spec_id}/edit', spec_edit, methods=['GET']),
    Route('/fragments/spec/{spec_id}', spec_patch, methods=['PATCH']),
]
