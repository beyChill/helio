from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from time import strftime

from stardust.config.constants import DataFFmpeg
from stardust.config.settings import get_setting

config = get_setting()


@dataclass(slots=True)
class FFmpegData:
    r"""Compile streamer data required for FFmpeg capture."""

    name_: str
    url_: str
    site: str = field(default="Chaturbate", init=False)
    file: Path = field(init=False)
    metadata: list = field(init=False)
    ffmpeg_: list = field(init=False)
    return_data: DataFFmpeg = field(init=False)

    def __post_init__(self):
        # self.config = get_setting()
        self._create_folder()
        self._set_metadata()
        self._ffmpeg_args()
        self.return_data = DataFFmpeg(
            name_=self.name_, url_=self.url_, file_=self.file, args=self.ffmpeg_
        )
        del self

    def _create_folder(self):
        file_path = self._make_path()
        filename = self._make_filename()
        self.file = Path(file_path / filename)

    def _make_path(self):
        dir_ = config.DIR_SSD
        video_folder = Path(dir_, self.site, self.name_)
        video_folder.mkdir(parents=True, exist_ok=True)
        return video_folder

    def _make_filename(self):
        return f"{self.name_} [CB] {self.now_()}.{config.VIDEO_EXT}"

    def now_(self):
        return str(strftime("(%Y-%m-%d) %H%M%S"))

    def _set_metadata(self):
        metadata = []
        today_ = date.today()
        today_str = str(today_)

        meta = {
            "title": f"{self.name_} - {today_str}",
            "author": f"{self.name_}",
            "album_artist": f"{self.name_}",
            "publisher": f"{self.site}",
            "description": f"{self.name_} live cam performance on {today_}",
            "genre": "webcam",
            "copyright": "Creative Commons",
            "album": f"{self.name_} {self.site}",
            "date": f"{today_}",
            "year": f"{today_str}",
            "service_provider": "python3",
            "encoder": "x264",
        }

        # format for ffmpeg
        for key, value in meta.items():
            metadata.extend(["-metadata", f"{key}={value}"])

        self.metadata = metadata

    def _ffmpeg_args(self):
        args = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-progress",
            "pipe:1",
            "-i",
            self.url_,
            *self.metadata,
            "-t",
            f"{config.VIDEO_LENGTH_SECONDS}",
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            self.file,
        ]
        self.ffmpeg_ = args

    def return_streamer(self):
        return self.return_data
