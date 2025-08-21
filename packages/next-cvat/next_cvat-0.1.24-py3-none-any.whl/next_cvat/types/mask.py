from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
from cvat_sdk.api_client import models
from PIL import Image
from pydantic import BaseModel

from .attribute import Attribute


class Mask(BaseModel):
    """A binary mask annotation in CVAT.
    
    Masks are used to store pixel-wise segmentations efficiently using run-length encoding (RLE).
    They can be created from numpy arrays or PIL Images and support various operations.
    
    Attributes:
        label: The label/class name for this mask
        source: The source of this annotation (e.g. "manual", "automatic")
        occluded: Whether this mask is occluded (0 for no, 1 for yes)
        z_order: The z-order/layer of this mask
        rle: Run-length encoded string representing the mask
        top: Top coordinate of the mask's bounding box
        left: Left coordinate of the mask's bounding box
        height: Height of the mask's bounding box
        width: Width of the mask's bounding box
        attributes: List of additional attributes for this mask
    """
    label: str
    source: str
    occluded: int
    z_order: int
    rle: str
    top: int
    left: int
    height: int
    width: int
    attributes: List[Attribute]

    @classmethod
    def from_segmentation(
        cls,
        segmentation: np.ndarray | Image.Image,
        label: str,
        source: str = "next-cvat",
        occluded: int = 0,
        z_order: int = 0,
        attributes: List[Attribute] = [],
    ) -> Mask:
        """Create a Mask from a segmentation array or image.
        
        Args:
            segmentation: Boolean numpy array or PIL Image to convert to mask
            label: The label/class name for this mask
            source: The source of this annotation (default: "next-cvat")
            occluded: Whether this mask is occluded (default: 0)
            z_order: The z-order/layer of this mask (default: 0)
            attributes: List of additional attributes (default: [])
            
        Returns:
            A new Mask instance
            
        Raises:
            ValueError: If the segmentation is empty (all False)
        """
        if isinstance(segmentation, Image.Image):
            segmentation = np.array(segmentation)

        # Handle RGB/RGBA images by taking mean across color channels
        if len(segmentation.shape) == 3:
            segmentation = segmentation.mean(axis=2) > 0
        else:
            segmentation = segmentation > 0

        # Find the bounding box of the segmentation
        rows = np.any(segmentation, axis=1)
        cols = np.any(segmentation, axis=0)

        if not np.any(rows) or not np.any(cols):
            raise ValueError("Cannot create mask from empty segmentation")

        top = np.where(rows)[0][0]
        bottom = np.where(rows)[0][-1] + 1
        left = np.where(cols)[0][0]
        right = np.where(cols)[0][-1] + 1

        height = bottom - top
        width = right - left

        crop = segmentation[top:bottom, left:right]
        rle = cls.rle_encode(crop)

        return cls(
            label=label,
            source=source,
            occluded=occluded,
            z_order=z_order,
            rle=rle,
            top=top,
            left=left,
            height=height,
            width=width,
            attributes=attributes,
        )

    def segmentation(self, height: int, width: int) -> np.ndarray:
        """Create a boolean segmentation mask.
        
        Args:
            height: Height of the output mask
            width: Width of the output mask
            
        Returns:
            A numpy 2D array of booleans where True indicates the mask
        """
        small_mask = self.rle_decode()
        mask = np.zeros((height, width), dtype=bool)
        mask[self.top : self.top + self.height, self.left : self.left + self.width] = (
            small_mask
        )
        return mask

    def rle_decode_slow(self) -> np.ndarray:
        """Original slower but verified RLE decoding implementation.
        
        This method is kept for reference and verification purposes.
        For normal use, use rle_decode() instead.
        
        Returns:
            A numpy 2D array of booleans representing the decoded mask
        """
        s = self.rle.split(",")
        mask = np.empty((self.height * self.width), dtype=bool)
        index = 0
        for i in range(len(s)):
            if i % 2 == 0:
                mask[index : index + int(s[i])] = False
            else:
                mask[index : index + int(s[i])] = True
            index += int(s[i])
        return mask.reshape(self.height, self.width)

    @classmethod
    def rle_encode_slow(cls, mask: np.ndarray) -> str:
        """Original slower but verified RLE encoding implementation.
        
        This method is kept for reference and verification purposes.
        For normal use, use rle_encode() instead.
        
        Args:
            mask: Boolean numpy array to encode
            
        Returns:
            RLE-encoded string representation of the mask
        """
        flat_mask = mask.flatten(order="C")
        counts = []
        prev_pixel = flat_mask[0]
        count = 1

        for pixel in flat_mask[1:]:
            if pixel == prev_pixel:
                count += 1
            else:
                counts.append(count)
                count = 1
                prev_pixel = pixel
        counts.append(count)

        if flat_mask[0]:
            counts = [0] + counts

        return ",".join(map(str, counts))

    def rle_decode(self) -> np.ndarray:
        """Optimized RLE decoding implementation.
        
        This is the preferred method for decoding RLE masks.
        
        Returns:
            A numpy 2D array of booleans representing the decoded mask
        """
        counts = np.array([int(x) for x in self.rle.split(",")])
        total_pixels = self.height * self.width
        
        # Calculate positions where values change
        positions = np.cumsum(counts)
        
        # Create an array of indices
        indices = np.arange(total_pixels)
        
        # Calculate which segment each index belongs to
        segment_indices = np.searchsorted(positions, indices, side='right')
        
        # Odd-numbered segments should be True
        mask = segment_indices % 2 == 1
        
        return mask.reshape(self.height, self.width)

    @classmethod
    def rle_encode(cls, mask: np.ndarray) -> str:
        """Optimized RLE encoding implementation.
        
        This is the preferred method for encoding RLE masks.
        
        Args:
            mask: Boolean numpy array to encode
            
        Returns:
            RLE-encoded string representation of the mask
        """
        flat_mask = mask.ravel()  # faster than flatten()
        if len(flat_mask) == 0:
            return "0"

        # Find runs using concatenated array trick
        n = len(flat_mask)
        runs = np.concatenate(
            ([0], np.where(flat_mask[1:] != flat_mask[:-1])[0] + 1, [n])
        )
        counts = np.diff(runs)

        # Handle case where mask starts with True
        if flat_mask[0]:
            counts = np.concatenate(([0], counts))

        return ",".join(map(str, counts))

    def request(
        self,
        frame: int,
        label_id: int,
        group: int = 0,
    ) -> models.LabeledShapeRequest:
        """Convert the mask to a CVAT shape format.

        Args:
            frame: The frame number this mask appears in
            label_id: The ID of the label this mask is associated with
            group: The group ID for this shape (default: 0)

        Returns:
            LabeledShapeRequest object for CVAT API
        """
        # Convert RLE string to list of floats
        points = [float(x) for x in self.rle.split(",")]

        # Use the stored dimensions for bounding box
        right = self.left + self.width - 1  # Subtract 1 because coordinates are 0-based
        bottom = (
            self.top + self.height - 1
        )  # Subtract 1 because coordinates are 0-based

        # Add bounding box coordinates
        points.extend(
            [
                float(self.left),  # x-offset
                float(self.top),  # y-offset
                float(right),  # right coordinate
                float(bottom),  # bottom coordinate
            ]
        )

        return models.LabeledShapeRequest(
            type="mask",
            occluded=bool(self.occluded),
            z_order=self.z_order,
            points=points,
            rotation=0.0,
            outside=False,
            attributes=[attr.model_dump() for attr in self.attributes],
            group=group,
            source=self.source,
            frame=frame,
            label_id=label_id,
        )

    def pil_image(
        self, height: int | None = None, width: int | None = None
    ) -> Image.Image:
        """Convert the mask to a PIL Image.

        Args:
            height: Optional height of the output image. If None, uses the mask's height
            width: Optional width of the output image. If None, uses the mask's width

        Returns:
            PIL Image containing the mask (black and white)
        """
        if height is None and width is None:
            # If no dimensions provided, use the cropped mask
            mask_array = self.rle_decode()
        else:
            # If dimensions provided, use full segmentation
            mask_array = self.segmentation(
                height=height or self.height, width=width or self.width
            )

        # Convert boolean array to uint8 (0 and 255)
        mask_array = mask_array.astype(np.uint8) * 255
        return Image.fromarray(mask_array, mode="L")

    def _repr_html_(self) -> str:
        """Generate HTML representation for Jupyter notebooks.
        
        Returns:
            HTML string containing an image of the mask and its metadata
        """
        img = self.pil_image()
        import base64
        from io import BytesIO

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return f"""
        <div style="
            border: 1px solid #ccc;
            padding: 10px;
            display: inline-block;
            border-radius: 5px;
            margin: 5px;
        ">
            <div>
                <strong>Label:</strong> {self.label}<br>
                <strong>Source:</strong> {self.source}<br>
                <strong>Size:</strong> {self.width}x{self.height}<br>
                <strong>Position:</strong> ({self.left}, {self.top})<br>
            </div>
            <div style="margin-top: 10px;">
                <img src="data:image/png;base64,{img_str}"
                     style="max-width: 300px; max-height: 300px;">
            </div>
        </div>
        """


def test_rle_decode_encode():
    """
    Test that decoding an RLE string and then encoding the mask returns the original RLE string.
    """
    import numpy as np

    # Corrected RLE string with counts summing to 15 (total pixels)
    original_rle = "0,3,2,5,4,1"
    height = 5
    width = 3  # Total pixels = 15

    # Create a Mask instance with the original RLE
    mask_instance = Mask(
        label="test",
        source="test",
        occluded=0,
        z_order=0,
        rle=original_rle,
        top=0,
        left=0,
        height=height,
        width=width,
        attributes=[],
    )

    # Decode the RLE string to get the mask
    decoded_mask = mask_instance.rle_decode()

    # Encode the mask back into an RLE string
    encoded_rle = mask_instance.rle_encode(decoded_mask)

    # Verify that the original and encoded RLE strings are the same
    assert original_rle == encoded_rle, (
        f"The encoded RLE does not match the original RLE.\n"
        f"Original RLE: {original_rle}\n"
        f"Encoded RLE: {encoded_rle}"
    )


def generate_random_rle(height, width):
    import numpy as np

    # Create a random binary mask
    mask = np.random.choice([False, True], size=(height, width))

    # Flatten the mask and encode it into an RLE string
    flat_mask = mask.flatten(order="C")
    counts = []
    prev_pixel = flat_mask[0]
    count = 1

    for pixel in flat_mask[1:]:
        if pixel == prev_pixel:
            count += 1
        else:
            counts.append(count)
            count = 1
            prev_pixel = pixel
    counts.append(count)

    if flat_mask[0]:
        counts = [0] + counts

    rle_string = ",".join(map(str, counts))
    return rle_string, height, width


def test_rle_decode_encode_random():
    """
    Test that decoding and then encoding a random RLE string returns the original RLE string.
    """

    # Generate a random RLE string
    height, width = 10, 10
    original_rle, height, width = generate_random_rle(height, width)

    # Create a Mask instance
    mask_instance = Mask(
        label="test",
        source="test",
        occluded=0,
        z_order=0,
        rle=original_rle,
        top=0,
        left=0,
        height=height,
        width=width,
        attributes=[],
    )

    # Decode and then encode the RLE string
    decoded_mask = mask_instance.rle_decode()
    encoded_rle = mask_instance.rle_encode(decoded_mask)

    # Verify that the original and encoded RLE strings are the same
    assert (
        original_rle == encoded_rle
    ), "The encoded RLE does not match the original RLE."
