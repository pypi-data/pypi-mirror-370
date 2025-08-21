from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from .box import Box
from .ellipse import Ellipse
from .mask import Mask
from .polygon import Polygon
from .polyline import Polyline
from .tag import Tag


class ImageAnnotation(BaseModel):
    """Annotation data for a single image in CVAT.

    Contains all annotation shapes (boxes, polygons, masks, polylines, ellipses) associated with an image.

    Attributes:
        id: Unique identifier for the image
        name: Filename of the image
        subset: Optional subset the image belongs to (e.g., "train", "test")
        task_id: ID of the task this image belongs to
        job_id: ID of the job this image belongs to
        width: Image width in pixels
        height: Image height in pixels
        boxes: List of bounding box annotations
        polygons: List of polygon annotations
        masks: List of mask annotations
        polylines: List of polyline annotations
        ellipses: List of ellipse annotations
        tags: List of tag annotations

    Example:
        ```python
        image = ImageAnnotation(
            id="1",
            name="frame_000001.jpg",
            subset="train",
            task_id="906591",
            job_id="1247749",
            width=1920,
            height=1080,
            boxes=[
                Box(label="car", xtl=100, ytl=200, xbr=300, ybr=400)
            ],
            masks=[
                Mask(label="person", points="100,200;300,400", z_order=1)
            ],
            ellipses=[
                Ellipse(label="defect", cx=500, cy=600, rx=50, ry=30)
            ],
            tags=[
                Tag(label="interesting", source="manual", attributes=[])
            ]
        )
        ```
    """

    id: str
    name: str
    subset: Optional[str] = None
    task_id: Optional[str] = None
    job_id: Optional[str] = None
    width: int
    height: int
    boxes: List[Box] = []
    polygons: List[Polygon] = []
    masks: List[Mask] = []
    polylines: List[Polyline] = []
    ellipses: List[Ellipse] = []
    tags: List[Tag] = []
