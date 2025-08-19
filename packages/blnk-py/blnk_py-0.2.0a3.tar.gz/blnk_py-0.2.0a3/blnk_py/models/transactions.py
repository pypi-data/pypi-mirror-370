from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
class Destination(BaseModel):
    identifier: str
    distribution: float | str
    narration: Optional[str] = None
class Source(BaseModel):
    identifier: str
    distribution: float | str
    narration: Optional[str] = None
class TransactionCreate(BaseModel):
    source: Optional[str] = None
    destination: Optional[str] = None
    sources: Optional[List[Source]] = None
    destinations: Optional[List[Destination]] = None
    amount: float
    precision: int = 100
    reference: str
    currency: str = 'GHS'
    description: Optional[str] = None
    inflight: bool = False
    meta_data: Dict[str, Any] = Field(default_factory=dict)
class Transaction(BaseModel):
    id: str
    reference: str
    status: str
    amount: float
    precision: int
    currency: str
    source: Optional[str] = None
    destination: Optional[str] = None
    created_at: str
    applied_at: Optional[str] = None
    parent_transaction: Optional[str] = None
    meta_data: Dict[str, Any] = Field(default_factory=dict)
class InflightUpdate(BaseModel):
    status: str
class RefundRequest(BaseModel):
    reason: Optional[str] = None
    meta_data: Dict[str, Any] = Field(default_factory=dict)
