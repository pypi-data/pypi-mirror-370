from __future__ import annotations

from typing import TYPE_CHECKING

from cvat_sdk.api_client import models
from PIL import Image
from pydantic import BaseModel

if TYPE_CHECKING:
    from .task import Task


class Frame(BaseModel, arbitrary_types_allowed=True):
    task: Task
    id: int
    frame_info: models.IFrameMeta

    @property
    def cvat(self) -> models.IFrameMeta:
        return self.frame_info

    def pil_image(self) -> Image.Image:
        with self.task.cvat() as cvat_task:
            frame_bytes = cvat_task.get_frame(self.id)
            return Image.open(frame_bytes)

    def _repr_html_(self) -> str:
        img = self.pil_image()
        import base64
        from io import BytesIO

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return f"""
        <div style="
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 800px;
            margin: 20px 0;
            background: #f8f9fa;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="
                padding: 15px;
                background: #ffffff;
                border-bottom: 1px solid #eee;">
                <div style="color: #444; line-height: 1.6;">
                    <span style="color: #666; display: inline-block; width: 80px;">ID:</span>
                    <span style="font-weight: 500;">{self.id}</span><br>
                    <span style="color: #666; display: inline-block; width: 80px;">Name:</span>
                    <span style="font-weight: 500;">{self.frame_info.name if self.frame_info.name else 'N/A'}</span><br>
                    <span style="color: #666; display: inline-block; width: 80px;">Size:</span>
                    <span style="font-weight: 500;">{self.frame_info.width} × {self.frame_info.height}px</span>
                </div>
            </div>
            <div style="padding: 15px; text-align: center;">
                <img src="data:image/png;base64,{img_str}" 
                     style="max-width: 100%; height: auto; border-radius: 4px;" />
            </div>
        </div>
        """
