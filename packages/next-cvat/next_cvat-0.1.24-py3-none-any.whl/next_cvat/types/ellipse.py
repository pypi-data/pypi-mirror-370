from __future__ import annotations

import math
from typing import List, Tuple

import numpy as np
from pydantic import BaseModel

from .attribute import Attribute
from .polygon import Polygon


class Ellipse(BaseModel):
    """Ellipse annotation in CVAT.

    Represents an ellipse shape annotation with center point (cx, cy) and radii (rx, ry).

    Attributes:
        label: Label name for the ellipse
        source: Source of the annotation (e.g., "manual")
        occluded: Whether the ellipse is occluded
        cx: X-coordinate of ellipse center
        cy: Y-coordinate of ellipse center
        rx: Radius in X direction
        ry: Radius in Y direction
        z_order: Z-order of the ellipse (drawing order)
        attributes: List of attributes associated with the ellipse

    Example:
        ```python
        ellipse = Ellipse(
            label="Deformation",
            source="manual",
            occluded=0,
            cx=3126.92,
            cy=509.86,
            rx=39.99,
            ry=18.92,
            z_order=0,
            attributes=[
                Attribute(name="Damage Level", value="0")
            ]
        )
        ```
    """

    label: str
    source: str = "manual"
    occluded: int = 0
    cx: float
    cy: float
    rx: float
    ry: float
    z_order: int = 0
    attributes: List[Attribute] = []

    def polygon(self, num_points: int = 32) -> Polygon:
        """Convert the ellipse to a polygon approximation.

        Args:
            num_points: Number of points to use for the polygon approximation.
                       More points = better approximation but slower processing.

        Returns:
            A Polygon instance approximating the ellipse shape
        """
        # Generate points around the ellipse using parametric equations
        points: List[Tuple[float, float]] = []
        for i in range(num_points):
            theta = 2 * math.pi * i / num_points
            x = self.cx + self.rx * math.cos(theta)
            y = self.cy + self.ry * math.sin(theta)
            points.append((x, y))

        return Polygon(
            label=self.label,
            source=self.source,
            occluded=self.occluded,
            points=points,
            z_order=self.z_order,
            attributes=self.attributes,
        )

    def segmentation(self, height: int, width: int) -> np.ndarray:
        """Create a boolean segmentation mask for the ellipse.

        Args:
            height: Height of the output mask
            width: Width of the output mask

        Returns:
            A numpy 2D array of booleans where True indicates the ellipse interior
        """
        # Create coordinate grids
        y, x = np.ogrid[:height, :width]

        # Ellipse equation: ((x-h)/rx)^2 + ((y-k)/ry)^2 <= 1
        # where (h,k) is the center
        mask = ((x - self.cx) / self.rx) ** 2 + ((y - self.cy) / self.ry) ** 2 <= 1
        return mask
