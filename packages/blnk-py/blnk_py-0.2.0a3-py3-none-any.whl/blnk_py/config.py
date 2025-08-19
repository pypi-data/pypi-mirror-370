from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    api_key: str
    base_url: str = 'http://localhost:9999'
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_backoff_seconds: float = 0.5
    user_agent: str = 'blnk-py/0.2.0a3 (+https://github.com/example/blnk-py)'
