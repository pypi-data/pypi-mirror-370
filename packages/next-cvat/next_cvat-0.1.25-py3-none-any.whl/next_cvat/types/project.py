from __future__ import annotations

from typing import List

from pydantic import BaseModel

from .label import Label


class Project(BaseModel):
    """A CVAT project containing tasks and labels.

    Attributes:
        id: Unique identifier for the project
        name: Human-readable name of the project
        created: Timestamp when the project was created
        updated: Timestamp when the project was last updated
        labels: List of label definitions for the project

    Example:
        ```python
        project = Project(
            id="217969",
            name="My Project",
            created="2024-01-01 12:00:00.000000+00:00",
            updated="2024-01-01 12:00:00.000000+00:00",
            labels=[
                Label(name="car", color="#ff0000", type="any"),
                Label(name="person", color="#00ff00", type="any")
            ]
        )
        ```
    """

    id: str
    name: str
    created: str
    updated: str
    labels: List[Label]
