from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, HttpUrl


class URL(BaseModel):
    url: HttpUrl


class NameURL(BaseModel):
    name_: str
    url: HttpUrl


class PassNone(BaseModel):
    quit: list[str]


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


class StreamerWithPid(BaseModel):
    pid: int
    name_: str


class FailVideoContext(BaseModel):
    status: int
    detail: str
    code: str
    ts_context: str | None
    name_: str
