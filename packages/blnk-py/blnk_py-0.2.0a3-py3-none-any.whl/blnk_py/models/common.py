from __future__ import annotations
from typing import Any, Dict
from pydantic import BaseModel, Field, ConfigDict
class Meta(BaseModel):
    model_config = ConfigDict(extra='allow')
    data: Dict[str, Any] = Field(default_factory=dict)
