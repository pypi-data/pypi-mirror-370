from __future__ import annotations
from typing import Dict, Any
from ..http import AsyncHttp
class SearchResource:
    def __init__(self, http: AsyncHttp):
        self._http = http
    async def transactions(self, *, q: str = '*', filter_by: str | None = None, per_page: int = 50) -> Dict[str, Any]:
        payload = {'q': q, 'query_by': 'reference', 'per_page': per_page}
        if filter_by:
            payload['filter_by'] = filter_by
        return await self._http.request('POST', '/search/transactions', json=payload)
    async def balances(self, *, q: str = '*', per_page: int = 50) -> Dict[str, Any]:
        payload = {'q': q, 'per_page': per_page}
        return await self._http.request('POST', '/search/balances', json=payload)
