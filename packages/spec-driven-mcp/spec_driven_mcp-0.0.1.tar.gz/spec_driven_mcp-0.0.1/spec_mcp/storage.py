from __future__ import annotations
from .models import FeatureSpec, Requirement, AcceptanceCriterion, gen_id
from . import db
from typing import List

def create_feature(name: str, description: str, category: str = 'uncategorized') -> FeatureSpec:
    feat = FeatureSpec(id=gen_id('FEAT'), name=name, description=description, category=category)
    db.execute(
        "INSERT INTO features (id,name,description,category,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",
        (feat.id, feat.name, feat.description, feat.category, feat.status, feat.created_at.isoformat(), feat.updated_at.isoformat())
    )
    return feat

def add_requirement(feature_id: str, title: str, description: str) -> Requirement:
    req = Requirement(id=gen_id('REQ'), feature_id=feature_id, title=title, description=description)
    db.execute(
        "INSERT INTO requirements (id,feature_id,title,description,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",
        (req.id, feature_id, req.title, req.description, req.status, req.created_at.isoformat(), req.updated_at.isoformat())
    )
    return req

def add_criterion(requirement_id: str, description: str, given: str|None=None, when: str|None=None, then: str|None=None) -> AcceptanceCriterion:
    crit = AcceptanceCriterion(id=gen_id('CRIT'), requirement_id=requirement_id, description=description, given=given, when=when, then=then)
    db.execute(
        "INSERT INTO criteria (id,requirement_id,description,given,when_clause,then_clause,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (crit.id, requirement_id, crit.description, crit.given, crit.when, crit.then, crit.status, crit.created_at.isoformat(), crit.updated_at.isoformat())
    )
    return crit

def search(text: str):
    like = f"%{text.lower()}%"
    results: List[dict] = []
    for row in db.query("SELECT id,name,status FROM features WHERE lower(name) LIKE ? OR lower(description) LIKE ?", (like, like)):
        results.append({'type':'feature','id':row['id'],'name':row['name'],'status':row['status']})
    for row in db.query("SELECT id,feature_id,title,status FROM requirements WHERE lower(title) LIKE ? OR lower(description) LIKE ?", (like, like)):
        results.append({'type':'requirement','id':row['id'],'feature_id':row['feature_id'],'title':row['title'],'status':row['status']})
    for row in db.query("SELECT c.id,r.feature_id,c.requirement_id,c.description,c.status FROM criteria c JOIN requirements r ON r.id=c.requirement_id WHERE lower(c.description) LIKE ?", (like,)):
        results.append({'type':'criterion','id':row['id'],'feature_id':row['feature_id'],'requirement_id':row['requirement_id'],'status':row['status']})
    return results

def get_feature(feature_id: str) -> FeatureSpec|None:
    frow = db.query_one("SELECT * FROM features WHERE id=?", (feature_id,))
    if not frow:
        return None
    feat = FeatureSpec(id=frow['id'], name=frow['name'], description=frow['description'], category=frow['category'] if 'category' in frow.keys() else 'uncategorized', status=frow['status'], created_at=frow['created_at'], updated_at=frow['updated_at'])  # type: ignore[arg-type]
    req_rows = db.query("SELECT * FROM requirements WHERE feature_id=?", (feature_id,))
    reqs: List[Requirement] = []
    for r in req_rows:
        req = Requirement(id=r['id'], feature_id=r['feature_id'], title=r['title'], description=r['description'], status=r['status'], created_at=r['created_at'], updated_at=r['updated_at'])  # type: ignore[arg-type]
        crit_rows = db.query("SELECT * FROM criteria WHERE requirement_id=?", (r['id'],))
        crits: List[AcceptanceCriterion] = []
        for c in crit_rows:
            crits.append(AcceptanceCriterion(id=c['id'], requirement_id=c['requirement_id'], description=c['description'], given=c['given'], when=c['when_clause'], then=c['then_clause'], status=c['status'], created_at=c['created_at'], updated_at=c['updated_at']))  # type: ignore[arg-type]
        req.criteria = crits
        reqs.append(req)
    feat.requirements = reqs
    return feat

def list_features_summary():
    return db.query("SELECT id,name,category,status FROM features ORDER BY created_at DESC")
