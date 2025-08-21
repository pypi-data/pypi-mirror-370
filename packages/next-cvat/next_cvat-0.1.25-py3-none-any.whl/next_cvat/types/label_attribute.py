from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw
from pydantic import BaseModel, field_validator


class LabelAttribute(BaseModel):
    name: str
    mutable: Optional[str] = None
    input_type: Optional[str] = None
    default_value: Optional[str] = None
    values: Optional[str] = None
