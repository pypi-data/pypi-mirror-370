"""Starlette dashboard app (HTML UI).
   Based on the Tremor Overview template: https://overview.tremor.so/support
"""
from __future__ import annotations
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.routing import Route
from starlette.requests import Request
from . import db
from .api import routes as api_routes
from .queries import feature_rows, spec_row

BASE_CSS = """
<!DOCTYPE html><html lang='en' class='dark'><head><meta charset='utf-8'/><title>Specs Dashboard</title>
<script src=\"https://cdn.tailwindcss.com?plugins=typography\"></script>
<script src=\"https://unpkg.com/htmx.org@2.0.6\"></script>
<script defer src=\"https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js\"></script>
<script>tailwind.config={darkMode:'class'};</script>
<link rel='icon' href='data:,'>
<style>
 body { font-feature-settings: 'ss01','cv02'; }
 .status-chip{border-radius:9999px;padding:2px 8px;font-size:12px;font-weight:500;}
 .status-VERIFIED{background:#166534;color:#fff;}
 .status-FAILING{background:#881337;color:#fff;}
 .status-PARTIAL{background:#92400e;color:#fff;}
 .status-UNTESTED{background:#1e293b;color:#e2e8f0;}
 a{color:#60a5fa}
 .req-card{position:relative;}
 .req-header{border-bottom:1px solid #1e293b;padding-bottom:.25rem;margin-bottom:.5rem;}
 .criteria-list{background:rgba(15,23,42,0.6);border:1px dashed #334155;padding:.5rem .75rem;border-radius:.5rem;}
 .criteria-list h4{font-size:.65rem;letter-spacing:.05em;text-transform:uppercase;color:#64748b;margin:0 0 .25rem;font-weight:600;}
</style></head><body class='bg-gray-950 text-slate-100 min-h-screen'>
<div class='max-w-7xl mx-auto px-6 py-8'>
<header class='mb-10'>
  <div class='rounded-xl border border-slate-800 bg-gradient-to-br from-slate-900/80 to-slate-950/40 p-6 md:p-8 relative overflow-hidden'>
      <div class='absolute inset-0 pointer-events-none opacity-30 mix-blend-overlay'
           style="background:radial-gradient(circle at 30% 20%,rgba(56,189,248,.15),transparent 60%),radial-gradient(circle at 75% 60%,rgba(14,165,233,.08),transparent 55%);"></div>
      <div class='relative flex flex-col md:flex-row md:items-start md:justify-between gap-8'>
          <div class='space-y-3 max-w-2xl'>
              <div class='inline-flex items-center gap-2 text-[10px] font-mono tracking-wide uppercase text-sky-400/70 bg-sky-500/10 ring-1 ring-inset ring-sky-500/20 px-2 py-1 rounded-full'>
                  <span>Specs Core</span>
              </div>
              <h1 class='text-3xl md:text-4xl font-semibold tracking-tight'>Specification Dashboard</h1>
              <p class='text-sm md:text-base text-slate-400 leading-relaxed'>Real-time visibility into feature requirements, acceptance criteria, non-functional constraints & verification health for spec-driven development.</p>
          </div>
          <div class='flex flex-col gap-3 w-full md:w-auto'>
              <div class='flex gap-2 justify-start md:justify-end'>
                  <a href='/' class='inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-md bg-sky-600 hover:bg-sky-500 text-white shadow-sm shadow-sky-500/20'>Reload</a>
                  <a href='/features' class='inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 ring-1 ring-inset ring-slate-600/60'>Browse Features</a>
              </div>
              <div class='grid grid-cols-2 gap-2 text-[10px] text-slate-500 md:text-right'>
                  <div class='flex md:justify-end gap-1'><span class='h-2 w-2 rounded-full bg-emerald-500/80 mt-1'></span><span>Verified</span></div>
                  <div class='flex md:justify-end gap-1'><span class='h-2 w-2 rounded-full bg-rose-500/80 mt-1'></span><span>Failing</span></div>
                  <div class='flex md:justify-end gap-1'><span class='h-2 w-2 rounded-full bg-slate-500/80 mt-1'></span><span>Untested</span></div>
                  <div class='flex md:justify-end gap-1'><span class='h-2 w-2 rounded-full bg-amber-500/80 mt-1'></span><span>Partial</span></div>
              </div>
          </div>
      </div>
      <nav class='mt-8 border-b border-slate-800 flex gap-8 text-sm relative'
           x-data
           x-init='(function(){const p=location.pathname;document.querySelectorAll("[data-tab]").forEach(a=>{const active=((p==="/"&&a.dataset.tab==="overview")||(p.startsWith("/features")&&a.dataset.tab==="features")||(p.startsWith("/feature/")&&a.dataset.tab==="features")); if(active){a.dataset.active=true;} else {a.dataset.active=false;}})})();'>
          <a data-tab='overview' href='/' class='py-2 -mb-px border-b-2 border-transparent data-[active=true]:border-sky-500 data-[active=true]:text-slate-100 text-slate-400 hover:text-slate-200 transition-colors'>Overview</a>
          <a data-tab='features' href='/features' class='py-2 -mb-px border-b-2 border-transparent data-[active=true]:border-sky-500 data-[active=true]:text-slate-100 text-slate-400 hover:text-slate-200 transition-colors'>Features</a>
      </nav>
  </div>
</header>
<main class='space-y-10'>
"""

def _status_chip(status: str) -> str:
    return f"<span class='status-chip status-{status}'>{status}</span>"

def _page(html: str, q: str = "", summary: str = "") -> HTMLResponse:
    filled = BASE_CSS.replace('{q}', q)
    banner = f"<div class='mb-6 text-xs text-slate-400 font-mono'>{summary}</div>" if summary else ''
    script = """
<script>
    function SpecOverview(){
        return {
            summary: {},
            dist: {},
            trend: { series: [] },
            topFailing: [],
            recent: [],
            init(){
                this.loadSummary();
                this.loadDistribution();
                this.loadTrend();
                this.loadTopFailing();
                this.loadRecent();
            },
            fetchJson(u){ return fetch(u).then(r=>r.json()); },
            loadSummary(){ this.fetchJson('/api/metrics/summary').then(d=>{ this.summary = d; }); },
            loadDistribution(){ this.fetchJson('/api/metrics/status-distribution').then(d=>{ this.dist = d.by_kind || {}; }); },
            loadTrend(){ this.fetchJson('/api/metrics/events-trend?days=30').then(d=>{ this.trend = d; this.renderTrend(); }); },
            loadTopFailing(){ this.fetchJson('/api/metrics/top-failing?limit=15').then(d=>{ this.topFailing = d.items || []; }); },
            loadRecent(){
                // derive from last 200 events focusing on FAILED
                fetch('/api/specs?kind=AC').then(()=>{}); // placeholder warmup
                fetch('/api/metrics/events-trend?days=2').then(()=>{});
                // For simplicity query direct DB via new endpoint? none yet; fallback: not implemented fully
                fetch('/api/metrics/top-failing?limit=1').then(()=>{});
            },
            distTotal(){
                if(!this.summary.status_counts) return '';
                const s = this.summary.status_counts; return Object.values(s).reduce((a,b)=>a+b,0) + ' items';
            },
            statusRows(){
                const s = this.summary.status_counts || {}; const total = Object.values(s).reduce((a,b)=>a+b,0) || 1;
                const order = ['FAILING','UNTESTED','PARTIAL','VERIFIED'];
                const cls = {FAILING:'bg-rose-600',UNTESTED:'bg-slate-600',PARTIAL:'bg-amber-600',VERIFIED:'bg-emerald-600'};
                return order.filter(k=>k in s).map(k=>({ label:k, count:s[k], pct: (s[k]/total*100).toFixed(1), barClass: cls[k] }));
            },
            statusClass(st){ return {FAILING:'bg-rose-700/40 text-rose-300', VERIFIED:'bg-emerald-700/40 text-emerald-300', PARTIAL:'bg-amber-700/40 text-amber-300', UNTESTED:'bg-slate-700/40 text-slate-300'}[st] || 'bg-slate-700/40 text-slate-300'; },
            renderTrend(){
                const svg = this.$refs.trendChart; if(!svg) return; while(svg.firstChild) svg.removeChild(svg.firstChild);
                const data = this.trend.series || []; if(!data.length){ return; }
                const w = svg.clientWidth || 600; const h = svg.clientHeight || 200; const pad=20;
                const maxY = Math.max(1, ...data.map(d=>d.passed + d.failed));
                const scaleX = i => pad + (i/(data.length-1))*(w - pad*2);
                const scaleY = v => h - pad - (v/maxY)*(h - pad*2);
                function area(seriesKey, color){
                    let path=''; data.forEach((d,i)=>{ const v=d[seriesKey]; const x=scaleX(i); const y=scaleY(v); path += (i?'L':'M')+x+','+y; });
                    // baseline close
                    path += 'L'+scaleX(data.length-1)+','+scaleY(0)+'L'+scaleX(0)+','+scaleY(0)+'Z';
                    const p = document.createElementNS('http://www.w3.org/2000/svg','path');
                    p.setAttribute('d', path); p.setAttribute('fill', color); p.setAttribute('opacity','0.25');
                    svg.appendChild(p);
                }
                area('failed','#dc2626');
                area('passed','#16a34a');
                // line overlay
                function line(seriesKey,color){
                    let path=''; data.forEach((d,i)=>{ const v=d[seriesKey]; const x=scaleX(i); const y=scaleY(v); path += (i?'L':'M')+x+','+y; });
                    const p=document.createElementNS('http://www.w3.org/2000/svg','path'); p.setAttribute('d',path); p.setAttribute('fill','none'); p.setAttribute('stroke',color); p.setAttribute('stroke-width','2'); svg.appendChild(p);
                }
                line('failed','#dc2626'); line('passed','#16a34a');
                // axes minimal
                const axis=document.createElementNS('http://www.w3.org/2000/svg','line'); axis.setAttribute('x1',pad); axis.setAttribute('x2',w-pad); axis.setAttribute('y1',axis.getAttribute('y2')|| (h-pad)); axis.setAttribute('y2',h-pad); axis.setAttribute('stroke','#334155'); svg.appendChild(axis);
            }
        }
    }
        function FeaturesList(){
            return {
                features: [],
                init(){ this.reload(); },
                statusClass(st){ return {FAILING:'bg-rose-700/40 text-rose-300', VERIFIED:'bg-emerald-700/40 text-emerald-300', PARTIAL:'bg-amber-700/40 text-amber-300', UNTESTED:'bg-slate-700/40 text-slate-300'}[st] || 'bg-slate-700/40 text-slate-300'; },
                reload(){ fetch('/api/features').then(r=>r.json()).then(list=>{ const body=this.$refs.featuresBody; if(!body) return; body.innerHTML=''; list.forEach(f=>{ const counts=f.counts||{}; const tr=document.createElement('tr'); tr.className='border-b border-slate-800 last:border-0 hover:bg-slate-800/40'; tr.innerHTML=`<td class='py-1 pr-4'><a class='text-sky-400 hover:underline font-mono text-xs' href='/feature/${f.feature_key}'>${f.feature_key}</a></td><td class='py-1 pr-4 text-xs text-slate-300'>${f.name||''}</td><td class='py-1 pr-4 text-emerald-400 font-mono text-xs'>${counts.VERIFIED||0}</td><td class='py-1 pr-4 text-rose-400 font-mono text-xs'>${counts.FAILING||0}</td><td class='py-1 pr-4 text-slate-400 font-mono text-xs'>${counts.UNTESTED||0}</td><td class='py-1 pr-4 text-amber-400 font-mono text-xs'>${counts.PARTIAL||0}</td><td class='py-1'><span class='px-2 py-0.5 rounded text-[10px] ${this.statusClass(f.status)}'>${f.status}</span></td>`; body.appendChild(tr); }); }); }
            }
        }
        function FeatureDetail(featureKey){
            return {
                featureKey, requirements: [], editing:false, current:null, form:{ title:'', statement:'', override_status:'' },
                init(){ this.reload(); },
                fetch(u){ return fetch(u).then(r=>r.json()); },
                reload(){ this.fetch(`/api/features/${this.featureKey}/tree`).then(d=>{ this.requirements = (d.requirements||[]).map(r=>this._augment(r)); }); },
                effective(st, ov){ return ov || st; },
                _augment(r){ r.effective_status=this.effective(r.status,r.override_status); r.children=(r.children||[]).map(c=>{c.effective_status=this.effective(c.status,c.override_status); return c}); r.effective_status=this.effective(r.status,r.override_status); return r; },
                statusClass(st){ return {FAILING:'bg-rose-700/40 text-rose-300', VERIFIED:'bg-emerald-700/40 text-emerald-300', PARTIAL:'bg-amber-700/40 text-amber-300', UNTESTED:'bg-slate-700/40 text-slate-300'}[st] || 'bg-slate-700/40 text-slate-300'; },
                openEdit(item){ this.current=item; this.form.title=item.title||''; this.form.statement=item.statement||''; this.form.override_status=item.override_status||''; this.editing=true; },
                allowOverride(){ return this.current && !this.current.id.includes('-AC-') && this.current.id.startsWith('AC-')===false && this.current.id.indexOf('AC')!==0 && this.current.id.indexOf('AC_')!==0 && this.current.id.split('-')[0] !== 'AC' && this.current.kind !== 'AC'; },
                submitEdit(){ if(!this.current) return; const payload={ title:this.form.title, statement:this.form.statement, override_status: this.form.override_status || null, clear_override: this.form.override_status==='' };
                    fetch(`/api/specs/${this.current.id}`, { method:'PATCH', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)}).then(r=>r.json()).then(updated=>{ if(updated && !updated.error){ this.editing=false; this.reload(); }});
                }
            }
        }
</script>
"""
    return HTMLResponse(filled + banner + html + "</main></div>" + script + "</body></html>")

def _dashboard_home(request: Request):
    # Overview page content (moved out of BASE_CSS)
    html = """
    <div x-data='SpecOverview()' x-init='init()' class='space-y-10'>
        <section>
            <div class='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
                <div class='kpi-card relative rounded-lg border border-slate-800 bg-slate-900/60 p-4'><p class='text-xs uppercase tracking-wide text-slate-400 mb-1'>Features</p><h2 class='text-3xl font-semibold' x-text='summary.features ?? "–"'>–</h2></div>
                <div class='kpi-card relative rounded-lg border border-slate-800 bg-slate-900/60 p-4'><p class='text-xs uppercase tracking-wide text-slate-400 mb-1'>Requirements</p><h2 class='text-3xl font-semibold' x-text='summary.requirements ?? "–"'>–</h2></div>
                <div class='kpi-card relative rounded-lg border border-slate-800 bg-slate-900/60 p-4'><p class='text-xs uppercase tracking-wide text-slate-400 mb-1'>Acceptance Criteria</p><h2 class='text-3xl font-semibold' x-text='summary.acceptance_criteria ?? "–"'>–</h2></div>
                <div class='kpi-card relative rounded-lg border border-slate-800 bg-slate-900/60 p-4'><p class='text-xs uppercase tracking-wide text-slate-400 mb-1'>NFR</p><h2 class='text-3xl font-semibold' x-text='summary.nfr ?? "–"'>–</h2></div>
            </div>
        </section>
        <section class='grid gap-6 lg:grid-cols-5'>
            <div class='lg:col-span-2 space-y-4'>
                <div class='rounded-lg border border-slate-800 bg-slate-900/60 p-4'>
                    <div class='flex items-center justify-between mb-3'><h3 class='font-medium'>Status Distribution</h3><span class='text-xs text-slate-500' x-text='distTotal()'></span></div>
                    <div class='space-y-2'>
                        <template x-for='row in statusRows()' :key='row.label'>
                            <div>
                                <div class='flex justify-between text-xs mb-1'><span x-text='row.label'></span><span x-text='row.count'></span></div>
                                <div class='w-full h-2 rounded bg-slate-800 overflow-hidden'>
                                    <div class='h-full' :class='row.barClass' :style="`width: ${row.pct}%;`"></div>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>
                <div class='rounded-lg border border-slate-800 bg-slate-900/60 p-4'>
                    <div class='flex items-center justify-between mb-3'><h3 class='font-medium'>Recent Failures</h3><button class='text-xs text-slate-400 hover:text-slate-200' @click='loadRecent()'>Reload</button></div>
                    <ul class='divide-y divide-slate-800 text-xs max-h-56 overflow-y-auto' x-ref='recentList'>
                        <template x-for='ev in recent' :key='ev.id'>
                            <li class='py-1 flex gap-2'><span class='w-20 text-slate-500' x-text='ev.occurred_at'></span><code class='text-rose-400' x-text='ev.spec_id'></code><span class='flex-1 truncate' x-text='ev.source || ""'></span></li>
                        </template>
                        <template x-if='recent.length===0'><li class='py-4 text-slate-500 text-center'>No failures</li></template>
                    </ul>
                </div>
            </div>
            <div class='lg:col-span-3 rounded-lg border border-slate-800 bg-slate-900/60 p-4 flex flex-col'>
                <div class='flex items-center justify-between mb-3'><h3 class='font-medium'>Verification Trend (30d)</h3><span class='text-xs text-slate-500' x-text='trend.series.length + " days"'></span></div>
                <div class='flex-1'>
                    <svg x-ref='trendChart' class='w-full h-56'></svg>
                </div>
            </div>
        </section>
        <section>
            <div class='rounded-lg border border-slate-800 bg-slate-900/60 p-4'>
                <div class='flex items-center justify-between mb-3'><h3 class='font-medium'>Top Failing Requirements</h3><button class='text-xs text-slate-400 hover:text-slate-200' @click='loadTopFailing()'>Refresh</button></div>
                <div class='overflow-x-auto'>
                    <table class='w-full text-sm'>
                        <thead>
                            <tr class='text-xs text-slate-400 text-left border-b border-slate-800'>
                                <th class='py-1 pr-4'>Requirement</th>
                                <th class='py-1 pr-4'>Failing</th>
                                <th class='py-1 pr-4'>Verified</th>
                                <th class='py-1 pr-4'>Untested</th>
                                <th class='py-1 pr-4'>Total</th>
                                <th class='py-1'>Status</th>
                            </tr>
                        </thead>
                        <tbody x-ref='topFailingBody'>
                            <template x-for='r in topFailing' :key='r.id'>
                                <tr class='border-b border-slate-800 last:border-0 hover:bg-slate-800/40'>
                                    <td class='py-1 pr-4'><code class='text-rose-300' x-text='r.id'></code><div class='text-xs text-slate-400 truncate max-w-xs' x-text='r.title || ""'></div></td>
                                    <td class='py-1 pr-4 text-rose-400 font-mono' x-text='r.failing_children'></td>
                                    <td class='py-1 pr-4 text-emerald-400 font-mono' x-text='r.verified_children'></td>
                                    <td class='py-1 pr-4 text-slate-400 font-mono' x-text='r.untested_children'></td>
                                    <td class='py-1 pr-4 text-slate-200 font-mono' x-text='r.total_children'></td>
                                    <td class='py-1'><span class='px-2 py-0.5 rounded text-xs' :class='statusClass(r.status)' x-text='r.status'></span></td>
                                </tr>
                            </template>
                            <template x-if='topFailing.length===0'><tr><td colspan='6' class='py-6 text-center text-slate-500 text-xs'>No failing requirements 🎉</td></tr></template>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    </div>
    """
    return _page(html, q="", summary="")

def _features_page(request: Request):
    html = """
    <div x-data='FeaturesList()' x-init='init()' class='space-y-6'>
        <div class='flex items-center justify-between'>
            <h2 class='text-xl font-semibold'>All Features</h2>
            <button class='text-xs px-3 py-1.5 rounded bg-sky-600 hover:bg-sky-500 text-white' @click='reload()'>Reload</button>
        </div>
        <div class='rounded-lg border border-slate-800 bg-slate-900/60 p-4'>
            <div class='overflow-x-auto'>
                <table class='w-full text-sm'>
                    <thead>
                        <tr class='text-xs text-slate-400 text-left border-b border-slate-800'>
                            <th class='py-1 pr-4'>Feature</th>
                            <th class='py-1 pr-4'>Name</th>
                            <th class='py-1 pr-4'>Verified</th>
                            <th class='py-1 pr-4'>Failing</th>
                            <th class='py-1 pr-4'>Untested</th>
                            <th class='py-1 pr-4'>Partial</th>
                            <th class='py-1'>Status</th>
                        </tr>
                    </thead>
                    <tbody x-ref='featuresBody'></tbody>
                </table>
            </div>
        </div>
    </div>
    """
    return _page(html, summary="")

def _dashboard_feature(request: Request):
    feature_key = request.path_params['feature_key']
    feat = db.query_one("SELECT * FROM feature WHERE feature_key=?", (feature_key,))
    if not feat:
        return _page("<div class='prose prose-invert'><h1>Not found</h1><p><a href='/'>Back</a></p></div>")
    reqs = db.query(
        "SELECT id,title,status FROM spec_item WHERE feature_key=? AND kind='REQUIREMENT' ORDER BY id",
        (feature_key,),
    )
    req_html = []
    for r in reqs:
        leaves = db.query(
            "SELECT id,kind,title,status FROM spec_item WHERE parent_id=? ORDER BY id", (r['id'],)
        )
        crit_items = (
            "".join(
                f"<li class='py-1 border-b border-slate-800 last:border-0'><div class='flex items-start gap-2'><code class='text-sky-400'>{c['id']}</code><span class='flex-1 text-sm' hx-get='/fragments/spec/{c['id']}' hx-target='closest li' hx-swap='innerHTML' data-spec='{c['id']}'>{c['title']}</span>{_status_chip(c['status'])}</div></li>"
                for c in leaves
                if c['kind'] == 'AC'
            )
            or "<li class='py-2 text-slate-500 text-sm'>No acceptance criteria</li>"
        )
        nfr_items = "".join(
            f"<li class='py-1 border-b border-slate-800 last:border-0'><div class='flex items-start gap-2'><code class='text-amber-400'>{c['id']}</code><span class='flex-1 text-sm' hx-get='/fragments/spec/{c['id']}' hx-target='closest li' hx-swap='innerHTML' data-spec='{c['id']}'>{c['title']}</span>{_status_chip(c['status'])}</div></li>"
            for c in leaves
            if c['kind'] == 'NFR'
        )
        nfr_block = (
            f"<div class='criteria-list mt-3'><h4>NFRs</h4><ul class='divide-y divide-slate-800'>{nfr_items}</ul></div>"
            if nfr_items
            else ''
        )
        req_html.append(
            f"<section class='req-card rounded-lg border border-slate-800 bg-slate-900/50 p-4'>"
            f"<div class='req-header flex items-start justify-between gap-4'><div><h3 class='font-semibold text-slate-200'>{r['title']}</h3><p class='text-xs font-mono text-slate-500'>{r['id']}</p></div>{_status_chip(r['status'])}</div>"
            f"<div class='criteria-list'><h4>Acceptance Criteria</h4><ul class='divide-y divide-slate-800'>{crit_items}</ul></div>"
            f"{nfr_block}" "</section>"
        )
    top_nfrs = db.query(
        "SELECT id,title,status FROM spec_item WHERE feature_key=? AND kind='NFR' AND parent_id IS NULL",
        (feature_key,),
    )
    top_nfr_block = ''
    if top_nfrs:
        t_items = "".join(
            f"<li class='py-1 border-b border-slate-800 last:border-0'><div class='flex items-start gap-2'><code class='text-amber-400'>{n['id']}</code><span class='flex-1 text-sm' hx-get='/fragments/spec/{n['id']}' hx-target='closest li' hx-swap='innerHTML' data-spec='{n['id']}'>{n['title']}</span>{_status_chip(n['status'])}</div></li>"
            for n in top_nfrs
        )
        top_nfr_block = (
            f"<section class='req-card rounded-lg border border-amber-700/40 bg-amber-950/20 p-4'><div class='req-header flex items-start justify-between gap-4'><div><h3 class='font-semibold text-amber-300'>Top-level NFRs</h3></div></div><div class='criteria-list'><h4>NFRs</h4><ul class='divide-y divide-slate-800'>{t_items}</ul></div></section>"
        )
    html = (
        f"<article class='prose prose-invert max-w-none'>"
        f"<h1 class='mb-2'>{feat['name']}</h1>"
        f"<p class='text-sm font-mono text-slate-500'>{feat['feature_key']}</p>"
        f"</article>"
        f"<div class='mt-4 mb-8 flex items-center gap-4'>{_status_chip(feat['status'])}<a href='/' class='text-sm hover:underline ml-auto'>Back</a></div>"
        f"{top_nfr_block}"
        f"<div class='space-y-4 mt-6'>{''.join(req_html)}</div>"
    )
    return _page(html, summary='')

def _dashboard_refresh(request: Request):
    return RedirectResponse('/')

async def api_spec(request: Request):
    spec_id = request.path_params['spec_id']
    row = spec_row(spec_id)
    if not row:
        return JSONResponse({'error': 'not found'}, status_code=404)
    events = db.events_for_spec(spec_id, limit=25)
    return JSONResponse(
        {
            'id': row['id'],
            'kind': row['kind'],
            'status': row['status'],
            'statement': row['statement'],
            'events': [dict(e) for e in events],
        }
    )

async def api_verify(request: Request):
    data = await request.json()
    spec_id = data.get('spec_id')
    outcome = data.get('outcome')
    source = data.get('source')
    from .verification import record_verification
    res = record_verification(spec_id, outcome, source=source)
    return JSONResponse(res)

async def api_batch_verify(request: Request):
    data = await request.json()
    events = data if isinstance(data, list) else data.get('events', [])
    result = db.insert_events(events)
    return JSONResponse(result)

def _feature_detail(request: Request):
        feature_key = request.path_params['feature_key']
        feat = db.query_one("SELECT * FROM feature WHERE feature_key=?", (feature_key,))
        if not feat:
                return _page("<div class='p-8 text-center text-slate-400'>Feature not found</div>")
        # Data hydrated client side from /api/features/{feature_key}/tree
        html = f"""
        <div x-data='FeatureDetail("{feature_key}")' x-init='init()' class='space-y-8'>
            <div class='flex items-start justify-between gap-4'>
                <div>
                    <h1 class='text-2xl font-semibold'>{feat['name']}</h1>
                    <p class='text-xs font-mono text-slate-500'>{feat['feature_key']}</p>
                </div>
                <a href='/features' class='text-xs px-3 py-1.5 rounded border border-slate-700 hover:bg-slate-800'>Back</a>
            </div>
            <section class='rounded-lg border border-slate-800 bg-slate-900/60 p-4'>
                <div class='flex items-center justify-between mb-4'>
                    <h2 class='font-medium'>Requirements & Criteria</h2>
                    <button class='text-xs text-slate-400 hover:text-slate-200' @click='reload()'>Reload</button>
                </div>
                <template x-for='req in requirements' :key='req.id'>
                    <div class='mb-6 last:mb-0'>
                        <div class='flex items-start gap-3'>
                            <div>
                                <div class='flex items-center gap-2'>
                                    <code class='text-sky-400 text-sm' x-text='req.id'></code>
                                    <span class='px-2 py-0.5 rounded text-xs' :class='statusClass(req.effective_status)' x-text='req.effective_status'></span>
                                    <button class='text-xs text-slate-400 hover:text-slate-200 underline' @click='openEdit(req)'>Edit</button>
                                </div>
                                <h3 class='font-semibold leading-tight' x-text='req.title'></h3>
                            </div>
                        </div>
                        <p class='text-xs text-slate-400 mt-1 whitespace-pre-wrap' x-text='req.statement'></p>
                        <ul class='mt-3 space-y-1'>
                            <template x-for='c in req.children' :key='c.id'>
                                <li class='rounded border border-slate-800 bg-slate-900/50 px-3 py-2'>
                                    <div class='flex items-center gap-2'>
                                        <code class='text-amber-300 text-xs' x-text='c.id'></code>
                                        <span class='px-2 py-0.5 rounded text-[10px]' :class='statusClass(c.effective_status)' x-text='c.effective_status'></span>
                                        <button class='text-[10px] text-slate-400 hover:text-slate-200 underline' @click='openEdit(c)'>Edit</button>
                                    </div>
                                    <div class='text-xs text-slate-300' x-text='c.title'></div>
                                    <div class='text-[10px] text-slate-500 mt-1 whitespace-pre-wrap' x-text='c.statement'></div>
                                </li>
                            </template>
                        </ul>
                    </div>
                </template>
            </section>
            <div x-show='editing' class='fixed inset-0 bg-black/60 flex items-center justify-center p-4'>
                <form @submit.prevent='submitEdit' class='w-full max-w-lg rounded-lg border border-slate-700 bg-slate-900 p-6 space-y-4'>
                    <h3 class='font-semibold text-lg'>Edit <span x-text='current?.id'></span></h3>
                    <div class='space-y-1'>
                        <label class='text-xs text-slate-400'>Title</label>
                        <input x-model='form.title' class='w-full bg-slate-800 rounded border border-slate-600 px-2 py-1 text-sm'/>
                    </div>
                    <div class='space-y-1'>
                        <label class='text-xs text-slate-400'>Statement</label>
                        <textarea x-model='form.statement' rows='4' class='w-full bg-slate-800 rounded border border-slate-600 px-2 py-1 text-xs'></textarea>
                    </div>
                    <div class='space-y-1' x-show='allowOverride()'>
                        <label class='text-xs text-slate-400'>Override Status</label>
                        <select x-model='form.override_status' class='w-full bg-slate-800 rounded border border-slate-600 px-2 py-1 text-xs'>
                            <option value=''>-- none --</option>
                            <option>UNTESTED</option><option>FAILING</option><option>PARTIAL</option><option>VERIFIED</option>
                        </select>
                        <button type='button' class='text-[10px] text-amber-400 underline' @click='form.override_status=""'>Clear</button>
                    </div>
                    <div class='flex justify-end gap-2 pt-2'>
                        <button type='button' @click='editing=false' class='px-3 py-1 text-xs rounded border border-slate-600 hover:bg-slate-800'>Cancel</button>
                        <button type='submit' class='px-3 py-1 text-xs rounded bg-sky-600 hover:bg-sky-500 text-white'>Save</button>
                    </div>
                </form>
            </div>
        </div>
        """
        return _page(html, summary="")

dashboard_app = Starlette(
    debug=False,
    routes=[
        Route('/', _dashboard_home),
        Route('/features', _features_page),
        Route('/feature/{feature_key}', _feature_detail),
        Route('/refresh', _dashboard_refresh),
        Route('/api/spec/{spec_id}', api_spec),
        Route('/api/verify', api_verify, methods=['POST']),
        Route('/api/batch-verify', api_batch_verify, methods=['POST']),
    ]
    + api_routes,
)
