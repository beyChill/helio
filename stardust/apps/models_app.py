from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class ContactSheetModel(BaseModel):
    input_path: Path
    interval: int
    output_path: Path


class DataFFmpeg(BaseModel):
    """Data for capturing live stream"""

    name_: str
    slug: str
    site: str
    url: str
    file_: Path
    # For FFmpeg use
    args: list


class not200(BaseModel):
    name_: Optional[str] = None
    site: str
    code_: int
    reason: Optional[str] = None
