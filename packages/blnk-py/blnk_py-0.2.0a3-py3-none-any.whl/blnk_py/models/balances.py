from __future__ import annotations
from typing import Dict, Any
from pydantic import BaseModel, Field
class Balance(BaseModel):
    id: str
    ledger_id: str
    currency: str
    precision: int
    balance: float
    inflight_credit_balance: float = 0.0
    inflight_debit_balance: float = 0.0
    queued_credit_balance: float = 0.0
    queued_debit_balance: float = 0.0
    meta_data: Dict[str, Any] = Field(default_factory=dict)
class CreateBalance(BaseModel):
    ledger_id: str
    currency: str = 'GHS'
    precision: int = 100
    meta_data: Dict[str, Any] = Field(default_factory=dict)
