from __future__ import annotations
from enum import Enum
class TxStatus(str, Enum):
    QUEUED = 'queued'
    INFLIGHT = 'inflight'
    APPLIED = 'applied'
    VOID = 'void'
    REJECTED = 'rejected'
