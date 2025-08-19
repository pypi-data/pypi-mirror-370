from __future__ import annotations
from typing import Dict, Any
from pydantic import BaseModel, Field
class Ledger(BaseModel):
    id: str
    name: str
    currency: str
    precision: int
    meta_data: Dict[str, Any] = Field(default_factory=dict)
class CreateLedger(BaseModel):
    name: str
    currency: str = 'GHS'
    precision: int = 100
    meta_data: Dict[str, Any] = Field(default_factory=dict)
