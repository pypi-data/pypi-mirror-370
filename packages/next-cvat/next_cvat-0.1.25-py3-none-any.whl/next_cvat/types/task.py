from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw
from pydantic import BaseModel, field_validator


class Task(BaseModel):
    """A CVAT task representing a unit of work for annotation.

    Tasks are created within projects and contain images to be annotated.
    Each task can be split into multiple jobs for parallel annotation.

    Attributes:
        task_id: Unique identifier for the task
        name: Human-readable name of the task
        url: Optional URL to access the task's data or API endpoint

    Example:
        ```python
        task = Task(
            task_id="906591",
            name="Batch 1",
            url="https://app.cvat.ai/api/jobs/520016"
        )
        ```
    """

    task_id: str
    name: str
    url: Optional[str] = None

    def job_id(self) -> str:
        """
        Extracts the job ID from the given URL.
        Assumes the job ID is the last numeric part of the URL.
        """
        parts = self.url.rstrip("/").split("/")
        for part in reversed(parts):
            if part.isdigit():
                return part
        raise ValueError(f"Could not extract job ID from URL: {self.url}")
