from __future__ import annotations

from typing import List, Tuple

import numpy as np
from cvat_sdk.api_client import models
from PIL import Image, ImageDraw
from pydantic import BaseModel, field_validator

from .attribute import Attribute


class Polygon(BaseModel):
    """A polygon annotation in CVAT.

    Polygons are used to define regions in images using a series of connected points.
    They can be converted to segmentation masks and support various geometric operations.

    Attributes:
        label: The label/class name for this polygon
        source: The source of this annotation (e.g. "manual", "automatic")
        occluded: Whether this polygon is occluded (0 for no, 1 for yes)
        points: List of (x,y) coordinates defining the polygon vertices
        z_order: The z-order/layer of this polygon
        attributes: List of additional attributes for this polygon
    """

    label: str
    source: str
    occluded: int
    points: List[Tuple[float, float]]
    z_order: int
    attributes: List[Attribute]

    @field_validator("points", mode="before")
    def parse_points(cls, v):
        """Parse points from string format if needed.

        Handles conversion from CVAT's string format ("x1,y1;x2,y2;...") to list of tuples.
        """
        if isinstance(v, str):
            return [tuple(map(float, point.split(","))) for point in v.split(";")]
        else:
            return v

    def leftmost(self) -> float:
        """Get the leftmost x-coordinate of the polygon."""
        return min([x for x, _ in self.points])

    def rightmost(self) -> float:
        """Get the rightmost x-coordinate of the polygon."""
        return max([x for x, _ in self.points])

    def segmentation(self, height: int, width: int) -> np.ndarray:
        """Create a boolean segmentation mask for the polygon.

        Args:
            height: Height of the output mask
            width: Width of the output mask

        Returns:
            A numpy 2D array of booleans where True indicates the polygon interior
        """
        mask = Image.new("L", (width, height), 0)
        ImageDraw.Draw(mask).polygon(self.points, outline=1, fill=1)
        return np.array(mask).astype(bool)

    def translate(self, dx: int, dy: int) -> Polygon:
        """Translate the polygon by (dx, dy).

        Args:
            dx: Amount to translate in the x direction
            dy: Amount to translate in the y direction

        Returns:
            A new Polygon instance translated by the specified amount
        """
        return Polygon(
            label=self.label,
            source=self.source,
            occluded=self.occluded,
            points=[(x + dx, y + dy) for x, y in self.points],
            z_order=self.z_order,
            attributes=self.attributes,
        )

    def polygon(self) -> Polygon:
        """Get this polygon.

        This method exists for compatibility with other shape types that can be
        converted to polygons.

        Returns:
            This polygon instance
        """
        return self

    def request(
        self, frame: int, label_id: int, group: int = 0
    ) -> models.LabeledShapeRequest:
        """Convert the polygon to a CVAT shape format.

        Args:
            frame: The frame number this polygon appears in
            label_id: The ID of the label this polygon is associated with
            group: The group ID for this shape (default: 0)

        Returns:
            LabeledShapeRequest object for CVAT API
        """
        return models.LabeledShapeRequest(
            type="polygon",
            occluded=bool(self.occluded),
            points=np.array(self.points).flatten().tolist(),
            rotation=0.0,
            outside=False,
            attributes=[attr.model_dump() for attr in self.attributes],
            group=group,
            source=self.source,
            frame=frame,
            label_id=label_id,
        )
