from __future__ import annotations
from typing import Any, Optional

class BlnkError(Exception): ...
class AuthError(BlnkError): ...
class NotFoundError(BlnkError): ...
class RateLimitError(BlnkError):
    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after
class ApiError(BlnkError):
    def __init__(self, status_code: int, message: str, payload: Optional[Any] = None):
        super().__init__(f'{status_code}: {message}')
        self.status_code = status_code
        self.payload = payload
