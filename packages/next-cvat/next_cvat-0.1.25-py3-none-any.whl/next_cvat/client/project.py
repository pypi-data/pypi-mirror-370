from __future__ import annotations

import json
import tempfile
import zipfile
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Generator, Union

from cvat_sdk import Client as CVATClient
from cvat_sdk.api_client import models
from cvat_sdk.core.proxies.projects import Project as CVATProject
from pydantic import BaseModel

from ..types.job_status import JobStatus
from .task import Task

if TYPE_CHECKING:
    from next_cvat.client import Client


class Project(BaseModel):
    client: Client
    id: int

    @contextmanager
    def cvat(self) -> Generator[CVATProject, None, None]:
        with self.client.cvat_client() as client:
            yield client.projects.retrieve(self.id)

    def download_(self, dataset_path: Union[str, Path], include_images=True) -> Project:
        """Download project data to the specified path.

        Args:
            dataset_path: Path where to save the project data. Will create:
                - annotations.xml: Project annotations
                - images/: Directory containing all images
        """
        dataset_path = Path(dataset_path)
        dataset_path.mkdir(parents=True, exist_ok=True)

        print(f"Downloading project {self.id} to {dataset_path}")

        with self.cvat() as cvat_project:
            # Download dataset (includes both annotations and images)
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file_path = Path(temp_dir) / "dataset.zip"
                cvat_project.export_dataset(
                    format_name="CVAT for images 1.1",
                    filename=temp_file_path,
                    include_images=include_images,
                )

                # Extract contents
                with zipfile.ZipFile(temp_file_path, "r") as zip_ref:
                    zip_ref.extractall(dataset_path)

            # Get job status for all tasks
            job_status = []
            for cvat_task in cvat_project.get_tasks():
                task_name = cvat_task.name
                for job in cvat_task.get_jobs():
                    job_status.append(JobStatus.from_job(job, task_name))

            # Save job status
            with open(dataset_path / "job_status.json", "w") as f:
                json.dump([status.model_dump() for status in job_status], f)

        return self

    def create_task_(
        self,
        name: str,
        image_quality: int = 100,
    ) -> Task:
        """
        Create a new task in this project.

        Args:
            name: Name of the task
            image_quality: Image quality (0-100) for compressed images

        Returns:
            Task object representing the created task
        """
        with self.client.cvat_client() as client:
            # Get project details to get the organization ID
            project = client.projects.retrieve(self.id)

            # Set organization header
            client.api_client.set_default_header("X-Organization", "NextMLAB")

            # Create task in the project
            spec = models.TaskWriteRequest(
                name=name,
                project_id=self.id,
                organization=project.organization,
                image_quality=image_quality,
                status="annotation",
            )
            task = client.tasks.create(spec=spec)
            return Task(project=self, id=task.id)

    def task(self, task_id: int) -> Task:
        return Task(project=self, id=task_id)

    def tasks(self) -> list[Task]:
        with self.client.cvat_client() as cvat_client:
            project = cvat_client.projects.retrieve(self.id)
            return [Task(project=self, id=task.id) for task in project.get_tasks()]

    def __hash__(self) -> int:
        return hash(self.model_dump_json())

    @lru_cache
    def labels(
        self, id: int | None = None, name: str | None = None
    ) -> list[models.Label]:
        with self.cvat() as cvat_project:
            labels = cvat_project.get_labels()

            if id is not None:
                labels = [label for label in labels if label.id == id]

            if name is not None:
                labels = [label for label in labels if label.name == name]

            return labels

    def label(self, name: str) -> models.Label:
        labels = self.labels(name=name)

        if len(labels) == 0:
            raise ValueError(f"Label with name {name} not found")
        elif len(labels) >= 2:
            raise ValueError(f"Multiple labels found with name {name}")
        else:
            return labels[0]

    def delete_task_(self, task_id: int) -> None:
        """
        Delete a task from this project.

        Args:
            task_id: ID of the task to delete
        """
        with self.client.cvat_client() as client:
            client.tasks.remove_by_ids([task_id])
