from __future__ import annotations

from enum import Enum
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


class loglvl(Enum):
    NOTSET = 0
    CREATED = 1
    MOVED = 2
    TIMER = 3
    OFFLINE = 8
    STOPPED = 9
    DEBUG = 10
    MAXTIME = 12
    INFO = 20
    SUCCESS = 30
    CAPTURING = 31
    WARNING = 40
    ERROR = 50
    FAILURE = 51
