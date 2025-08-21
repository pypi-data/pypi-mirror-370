from __future__ import annotations

from typing import TYPE_CHECKING

from cvat_sdk.api_client import models
from pydantic import BaseModel

import next_cvat

if TYPE_CHECKING:
    from .job import Job


class JobAnnotations(BaseModel, arbitrary_types_allowed=True):
    job: Job
    annotations: dict

    def add_mask_(
        self,
        mask: next_cvat.Mask,
        image_name: str,
        group: int = 0,
    ) -> JobAnnotations:
        label = self.job.task.project.label(name=mask.label)

        frame = self.job.task.frame(image_name=image_name)

        self.annotations["shapes"].append(
            mask.request(
                frame=frame.id,
                label_id=label.id,
                group=group,
            )
        )

        return self

    def add_polyline_(
        self,
        polyline: next_cvat.Polyline,
        image_name: str,
        group: int = 0,
    ) -> JobAnnotations:
        label = self.job.task.project.label(name=polyline.label)

        frame = self.job.task.frame(image_name=image_name)

        self.annotations["shapes"].append(
            polyline.request(frame=frame.id, label_id=label.id, group=group)
        )

        return self

    def add_polygon_(
        self,
        polygon: next_cvat.Polygon,
        image_name: str,
        group: int = 0,
    ) -> JobAnnotations:
        label = self.job.task.project.label(name=polygon.label)

        frame = self.job.task.frame(image_name=image_name)

        self.annotations["shapes"].append(
            polygon.request(frame=frame.id, label_id=label.id, group=group)
        )

        return self

    def add_tag_(
        self,
        tag: next_cvat.Tag,
        image_name: str,
        group: int = 0,
    ) -> JobAnnotations:
        label = self.job.task.project.label(name=tag.label)

        frame = self.job.task.frame(image_name=image_name)

        self.annotations["tags"].append(
            tag.request(frame=frame.id, label_id=label.id, group=group)
        )

        return self

    def request(self) -> models.LabeledDataRequest:
        request = models.LabeledDataRequest()
        request.version = self.annotations["version"]

        return request
