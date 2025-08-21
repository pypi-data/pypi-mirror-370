from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator, Literal

from cvat_sdk.core.proxies.jobs import Job as CVATJob
from pydantic import BaseModel

from .job_annotations import JobAnnotations

if TYPE_CHECKING:
    from .task import Task


JobState = Literal["new", "in progress", "rejected", "completed"]
JobStage = Literal["annotation", "validation", "acceptance"]


class Job(BaseModel):
    task: Task
    id: int

    @contextmanager
    def cvat(self) -> Generator[CVATJob, None, None]:
        with self.task.project.client.cvat_client() as cvat_client:
            yield cvat_client.jobs.retrieve(self.id)

    def annotations(self) -> JobAnnotations:
        with self.task.project.client.cvat_client() as cvat_client:
            return JobAnnotations(
                job=self,
                annotations=cvat_client.jobs.retrieve(self.id)
                .get_annotations()
                .to_dict(),
            )

    def update_annotations_(self, annotations: JobAnnotations):
        with self.task.project.client.cvat_client() as cvat_client:
            annotations_request = annotations.request()
            return cvat_client.jobs.retrieve(self.id).set_annotations(
                annotations_request
            )

    def state(self) -> JobState:
        """Get the current state of the job (e.g., 'new', 'in progress', 'completed', 'rejected')."""
        with self.cvat() as job:
            return job.state

    def stage(self) -> JobStage:
        """Get the current stage of the job (e.g., 'annotation', 'validation', 'acceptance')."""
        with self.cvat() as job:
            return job.stage
