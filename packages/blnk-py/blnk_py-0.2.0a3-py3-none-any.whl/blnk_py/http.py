from __future__ import annotations
import asyncio, uuid
from typing import Any, Dict, Optional
import httpx
from .config import Config
from .errors import ApiError, AuthError, NotFoundError, RateLimitError

IDEMPOTENCY_HEADER = 'Idempotency-Key'

def _idempotency_key(key: Optional[str]) -> str:
    return key or str(uuid.uuid4())

class AsyncHttp:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._client = httpx.AsyncClient(base_url=cfg.base_url, timeout=cfg.timeout_seconds, headers={
            'Authorization': f'Bearer {cfg.api_key}',
            'User-Agent': cfg.user_agent,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

    async def request(self, method: str, path: str, *, json: Optional[Dict[str, Any]] = None,
                      idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        retries = 0
        while True:
            headers = {}
            if method.upper() in {'POST','PUT','PATCH'}:
                headers[IDEMPOTENCY_HEADER] = _idempotency_key(idempotency_key)
            resp = await self._client.request(method, path, json=json, headers=headers)
            if resp.status_code == 401:
                raise AuthError('Unauthorized (check API key)')
            if resp.status_code == 404:
                raise NotFoundError(f'Not found: {path}')
            if resp.status_code == 429:
                retry_after = float(resp.headers.get('Retry-After', self.cfg.retry_backoff_seconds))
                if retries >= self.cfg.max_retries:
                    raise RateLimitError('Rate limited', retry_after=retry_after)
                await asyncio.sleep(retry_after)
                retries += 1
                continue
            if 500 <= resp.status_code < 600:
                if retries >= self.cfg.max_retries:
                    raise ApiError(resp.status_code, 'Server error', resp.text)
                await asyncio.sleep(self.cfg.retry_backoff_seconds * (2 ** retries))
                retries += 1
                continue
            if not (200 <= resp.status_code < 300):
                raise ApiError(resp.status_code, 'API error', resp.text)
            return resp.json()

    async def aclose(self) -> None:
        await self._client.aclose()

class InAppAsyncHttp(AsyncHttp):
    def __init__(self, cfg: Config, app, base_prefix: str = ''):
        self.cfg = cfg
        self._base_prefix = base_prefix.rstrip('/')
        transport = httpx.ASGITransport(app=app)
        self._client = httpx.AsyncClient(transport=transport, base_url='http://in-app', headers={
            'Authorization': f'Bearer {cfg.api_key}',
            'User-Agent': cfg.user_agent,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

    async def request(self, method: str, path: str, *, json: Optional[Dict[str, Any]] = None,
                      idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        headers = { 'Idempotency-Key': _idempotency_key(idempotency_key) }
        full_path = f"{self._base_prefix}{path if path.startswith('/') else '/' + path}"
        resp = await self._client.request(method, full_path, json=json, headers=headers)
        if resp.status_code == 401:
            raise AuthError('Unauthorized (check API key)')
        if resp.status_code == 404:
            raise NotFoundError(f'Not found: {full_path}')
        if not (200 <= resp.status_code < 300):
            raise ApiError(resp.status_code, 'API error', resp.text)
        return resp.json()
