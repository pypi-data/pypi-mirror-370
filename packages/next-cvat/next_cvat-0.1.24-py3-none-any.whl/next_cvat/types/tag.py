from __future__ import annotations

from typing import List

from cvat_sdk.api_client import models
from pydantic import BaseModel

from .attribute import Attribute


class Tag(BaseModel):
    label: str
    source: str
    attributes: List[Attribute]

    def request(
        self, frame: int, label_id: int, group: int = 0
    ) -> models.LabeledImageRequest:
        return models.LabeledImageRequest(
            frame=frame,
            label_id=label_id,
            group=group,
            source=self.source,
            attributes=[attr.model_dump() for attr in self.attributes],
        )
