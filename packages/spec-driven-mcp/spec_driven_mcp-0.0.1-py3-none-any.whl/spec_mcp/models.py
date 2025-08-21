from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict
from datetime import datetime
import uuid

Status = Literal["UNTESTED","FAILING","PARTIAL","VERIFIED"]


def gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

class AcceptanceCriterion(BaseModel):
    id: str = Field(default_factory=lambda: gen_id("CRIT"))
    requirement_id: str
    description: str
    given: Optional[str] = None
    when: Optional[str] = None
    then: Optional[str] = None
    status: Status = "UNTESTED"
    tests: List[str] = Field(default_factory=list, description="IDs of linked tests")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Requirement(BaseModel):
    id: str = Field(default_factory=lambda: gen_id("REQ"))
    feature_id: str
    title: str
    description: str
    status: Status = "UNTESTED"
    criteria: List[AcceptanceCriterion] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FeatureSpec(BaseModel):
    id: str = Field(default_factory=lambda: gen_id("FEAT"))
    name: str
    description: str
    category: str = Field(default="uncategorized")
    status: Status = "UNTESTED"
    requirements: List[Requirement] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TestLink(BaseModel):
    id: str = Field(default_factory=lambda: gen_id("TESTLINK"))
    target_type: Literal["requirement","criterion"]
    target_id: str
    test_id: str
    last_result: Optional[Literal["passed","failed"]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DataStore(BaseModel):
    features: List[FeatureSpec] = Field(default_factory=list)

    def index_feature(self) -> Dict[str, FeatureSpec]:
        return {f.id: f for f in self.features}

    def find_requirement(self, req_id: str) -> Optional[Requirement]:
        for f in self.features:
            for r in f.requirements:
                if r.id == req_id:
                    return r
        return None

    def find_criterion(self, crit_id: str) -> Optional[AcceptanceCriterion]:
        for f in self.features:
            for r in f.requirements:
                for c in r.criteria:
                    if c.id == crit_id:
                        return c
        return None
