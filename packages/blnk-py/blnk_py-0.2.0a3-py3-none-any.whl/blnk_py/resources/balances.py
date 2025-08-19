from __future__ import annotations
from ..http import AsyncHttp
from ..models.balances import Balance, CreateBalance
class BalancesResource:
    def __init__(self, http: AsyncHttp):
        self._http = http
    async def get(self, balance_id: str, *, with_queued: bool = True) -> Balance:
        path = f"/balances/{balance_id}?with_queued={'true' if with_queued else 'false'}"
        data = await self._http.request('GET', path)
        return Balance.model_validate(data)
    async def get_at(self, balance_id: str, iso_timestamp: str) -> Balance:
        data = await self._http.request('GET', f'/balances/{balance_id}/at?timestamp={iso_timestamp}')
        return Balance.model_validate(data)
    async def create(self, body: CreateBalance) -> Balance:
        data = await self._http.request('POST', '/balances', json=body.model_dump())
        return Balance.model_validate(data)
