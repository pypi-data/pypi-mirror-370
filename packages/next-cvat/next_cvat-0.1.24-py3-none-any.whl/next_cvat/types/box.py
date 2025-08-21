from __future__ import annotations

from typing import List, Tuple

import numpy as np
from pydantic import BaseModel

from .attribute import Attribute
from .polygon import Polygon


class Box(BaseModel):
    """A bounding box annotation in CVAT.
    
    Boxes are used to define rectangular regions in images using top-left and bottom-right coordinates.
    They can be converted to polygons and segmentation masks.
    
    Attributes:
        label: The label/class name for this box
        xtl: X-coordinate of the top-left corner
        ytl: Y-coordinate of the top-left corner
        xbr: X-coordinate of the bottom-right corner
        ybr: Y-coordinate of the bottom-right corner
        occluded: Whether this box is occluded (0 for no, 1 for yes)
        z_order: The z-order/layer of this box
        source: The source of this annotation (e.g. "manual", "automatic")
        attributes: List of additional attributes for this box
    """
    label: str
    xtl: float
    ytl: float
    xbr: float
    ybr: float
    occluded: int
    z_order: int
    source: str = "manual"
    attributes: List[Attribute]

    def polygon(self) -> Polygon:
        """Convert the box to a polygon.
        
        Returns:
            A Polygon instance representing the box's corners
        """
        points = [
            (self.xtl, self.ytl),
            (self.xbr, self.ytl),
            (self.xbr, self.ybr),
            (self.xtl, self.ybr),
        ]
        return Polygon(
            label=self.label,
            source=self.source,
            occluded=self.occluded,
            points=points,
            z_order=self.z_order,
            attributes=self.attributes,
        )

    def segmentation(self, height: int, width: int) -> np.ndarray:
        """Create a boolean segmentation mask for the box.
        
        Args:
            height: Height of the output mask
            width: Width of the output mask
            
        Returns:
            A numpy 2D array of booleans where True indicates the box interior
        """
        return self.polygon().segmentation(height=height, width=width)
