from __future__ import annotations
from ..http import AsyncHttp
from ..models.ledgers import Ledger, CreateLedger
class LedgersResource:
    def __init__(self, http: AsyncHttp):
        self._http = http
    async def create(self, body: CreateLedger) -> Ledger:
        data = await self._http.request('POST', '/ledgers', json=body.model_dump())
        return Ledger.model_validate(data)
