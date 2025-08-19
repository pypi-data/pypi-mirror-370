from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
class ExternalRecord(BaseModel):
    id: str
    amount: float
    currency: str
    date: str
    reference: Optional[str] = None
    meta_data: Dict[str, Any] = Field(default_factory=dict)
class UploadExternalDataRequest(BaseModel):
    source: str
    records: List[ExternalRecord]
class MatchingCriterion(BaseModel):
    field: str
    operator: str
    allowable_drift: Optional[float] = None
class MatchingRule(BaseModel):
    name: str
    criteria: List[MatchingCriterion]
class StartReconciliationRequest(BaseModel):
    upload_id: str
    strategy: str
    grouping_criteria: Optional[str] = None
    matching_rule_ids: List[str]
    dry_run: bool = False
class ReconciliationRun(BaseModel):
    id: str
    status: str
    matched: int
    unmatched: int
