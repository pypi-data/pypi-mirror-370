from __future__ import annotations

from typing import List

from pydantic import BaseModel

from .label_attribute import LabelAttribute


class Label(BaseModel):
    name: str
    color: str
    type: str
    attributes: List[LabelAttribute]
