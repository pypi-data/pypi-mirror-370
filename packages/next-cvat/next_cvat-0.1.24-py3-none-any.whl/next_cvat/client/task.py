from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Generator, List, Union

from cvat_sdk.api_client.exceptions import ApiException
from cvat_sdk.api_client.model.data_request import DataRequest
from cvat_sdk.core.proxies.tasks import Task as CVATTask
from pydantic import BaseModel

from .frame import Frame
from .job import Job

if TYPE_CHECKING:
    from .project import Project


class Task(BaseModel):
    project: Project
    id: int

    @contextmanager
    def cvat(self) -> Generator[CVATTask, None, None]:
        with self.project.client.cvat_client() as cvat_client:
            yield cvat_client.tasks.retrieve(self.id)

    def create_job_(self, name: str):
        pass

    def job(self, job_id: int) -> Job:
        return Job(task=self, id=job_id)

    def jobs(self) -> list[Job]:
        """Get all jobs associated with this task."""
        with self.cvat() as cvat_task:
            return [Job(task=self, id=job.id) for job in cvat_task.get_jobs()]

    def frame(
        self,
        frame_id: int | None = None,
        name: str | None = None,
        image_name: str | None = None,
    ) -> Frame:
        params = {
            "frame_id": frame_id,
            "name": name,
            "image_name": image_name,
        }
        image_identifier_string = ", ".join(
            f"{k}={v}" for k, v in params.items() if v is not None
        )

        frames = self.frames()

        frames = [
            frame
            for frame in frames
            if (frame.id == frame_id or frame_id is None)
            and (frame.frame_info.name == name or name is None)
            and (Path(frame.frame_info.name).name == image_name or image_name is None)
        ]

        if len(frames) >= 2:
            raise ValueError(f"Multiple frames found for {image_identifier_string}")
        elif len(frames) == 0:
            raise ValueError(f"Frame for {image_identifier_string} not found")
        else:
            return frames[0]

    def __hash__(self) -> int:
        return hash(self.model_dump_json())

    @lru_cache
    def frames(self) -> list[Frame]:
        with self.cvat() as cvat_task:
            # Get task data directly
            task_data = cvat_task.get_meta()
            frames_info = task_data.frames
            deleted_frames = task_data._data_store.get("deleted_frames", [])
            # Only include frames that have not been deleted
            return [
                Frame(task=self, id=i, frame_info=frame_info)
                for i, frame_info in enumerate(frames_info)
                if i not in deleted_frames  # Skip deleted frames
            ]

    def upload_images_(
        self,
        image_paths: Union[str, Path, List[Union[str, Path]]],
        image_quality: int = 100,
    ) -> None:
        """
        Upload images to this task
        
        Args:
            image_paths: Path or list of paths to images
            image_quality: Image quality (0-100) for compressed images
        """
        if isinstance(image_paths, (str, Path)):
            image_paths = [image_paths]
        
        image_paths = [Path(p) for p in image_paths]
        
        with self.cvat() as cvat_task:
            cvat_task.upload_data(
                resources=image_paths,
                params={
                    "image_quality": image_quality,
                }
            )

    def delete_frame_(self, frame_id: int) -> None:
        """
        Delete a single frame from the task
        
        Args:
            frame_id: ID of the frame to delete (this is the frame index, 0-based)
            
        Raises:
            ValueError: If frame_id is invalid
            ApiException: If CVAT API call fails
        """
        with self.cvat() as cvat_task:
            try:
                print(f"Deleting frame {frame_id}...")
                
                # Get the frame name before deletion
                frames_before = cvat_task.get_frames_info()
                if frame_id >= len(frames_before):
                    raise ValueError(f"Frame with ID {frame_id} not found")
                frame_name = frames_before[frame_id].name
                print(f"Frame name: {frame_name}")
                
                # Delete the frame using remove_frames_by_ids
                # Note: frame_id is the frame index (0-based)
                cvat_task.remove_frames_by_ids([frame_id])
                
                # Wait for the deletion to complete
                print("Waiting for deletion to complete...")
                from time import sleep
                sleep(5)  # Give CVAT some time to process the deletion
                
                # Clear our frames cache since the frames have changed
                self.frames.cache_clear()
                print("Frame deleted successfully")
                return
                    
            except ApiException as e:
                if "frames with id" in str(e) and "were not found" in str(e):
                    raise ValueError(f"Frame with ID {frame_id} not found") from e
                raise
