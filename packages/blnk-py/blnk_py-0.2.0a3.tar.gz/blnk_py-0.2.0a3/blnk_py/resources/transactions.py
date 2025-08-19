from __future__ import annotations
from typing import Optional, Dict, Any
from ..http import AsyncHttp
from ..models.transactions import TransactionCreate, Transaction, InflightUpdate, RefundRequest
class TransactionsResource:
    def __init__(self, http: AsyncHttp):
        self._http = http
    async def create(self, body: TransactionCreate, *, idempotency_key: Optional[str] = None) -> Transaction:
        data = await self._http.request('POST', '/transactions', json=body.model_dump(), idempotency_key=idempotency_key)
        return Transaction.model_validate(data)
    async def commit_inflight(self, inflight_id: str) -> Transaction:
        payload = InflightUpdate(status='commit')
        data = await self._http.request('PUT', f'/transactions/inflight/{inflight_id}', json=payload.model_dump())
        return Transaction.model_validate(data)
    async def void_inflight(self, inflight_id: str) -> Transaction:
        payload = InflightUpdate(status='void')
        data = await self._http.request('PUT', f'/transactions/inflight/{inflight_id}', json=payload.model_dump())
        return Transaction.model_validate(data)
    async def refund(self, transaction_id: str, body: Optional[RefundRequest] = None) -> Dict[str, Any]:
        data = await self._http.request('POST', f'/refund-transaction/{transaction_id}', json=(body.model_dump() if body else {}))
        return data
