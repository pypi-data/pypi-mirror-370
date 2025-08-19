from __future__ import annotations
from ..http import AsyncHttp
from ..models.reconciliation import (
    UploadExternalDataRequest, MatchingRule, StartReconciliationRequest, ReconciliationRun
)
class ReconciliationResource:
    def __init__(self, http: AsyncHttp):
        self._http = http
    async def upload(self, req: UploadExternalDataRequest) -> dict:
        return await self._http.request('POST', '/reconciliation/upload', json=req.model_dump())
    async def create_rule(self, rule: MatchingRule) -> dict:
        return await self._http.request('POST', '/reconciliation/matching-rules', json=rule.model_dump())
    async def start(self, req: StartReconciliationRequest) -> ReconciliationRun:
        data = await self._http.request('POST', '/reconciliation/start', json=req.model_dump())
        return ReconciliationRun.model_validate(data)
    async def start_instant(self, external_payload: dict) -> ReconciliationRun:
        data = await self._http.request('POST', '/reconciliation/start-instant', json=external_payload)
        return ReconciliationRun.model_validate(data)
