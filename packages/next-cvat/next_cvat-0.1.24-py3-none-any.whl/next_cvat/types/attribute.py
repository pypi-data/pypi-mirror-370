from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Attribute(BaseModel):
    name: str
    value: Optional[str]
    spec_id: Optional[int] = None
