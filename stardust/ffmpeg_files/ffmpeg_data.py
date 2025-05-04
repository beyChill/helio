from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from time import strftime
from typing import NamedTuple, Optional
from stardust.apps import __apps__ as helio_apps
from stardust.config.constants import DataFFmpeg
from stardust.config.settings import get_setting

config = get_setting()


class AppID(NamedTuple):
    slug: str
    name_: Optional[str] = None
    color: Optional[str] = None


def get_app_id(app_tag: str):
    """
    Dynamically generate a dict then return value
    """
    APP_DICT = {}
    for app in dir(helio_apps):
        if app.startswith("app_"):
            app_data = getattr(helio_apps, app)
            APP_DICT[app_data[0]] = app_data

    if not (data := APP_DICT.get(app_tag)):
        return AppID(slug=app_tag)

    return AppID(*data)


@dataclass(slots=True)
class FFmpegConfig:
    """Compile streamer data required for FFmpeg capture."""

    name_: str
    slug: str
    url_: str
    site_id: AppID = field(init=False)
    site: str = field(init=False, default="Unknown")
    file: Path = field(init=False)
    metadata: list = field(init=False)
    ffmpeg_: list = field(init=False)
    return_data: DataFFmpeg = field(init=False)

    def __post_init__(self):
        self.site_id = get_app_id(self.slug)
        if self.site_id.name_:
            self.site = self.site_id.name_
        # self.config = get_setting()
        self._create_folder()
        self._set_metadata()
        self._ffmpeg_args()
        self.return_data = DataFFmpeg(
            name_=self.name_,
            slug=self.slug,
            site=self.site,
            url=self.url_,
            file_=self.file,
            args=self.ffmpeg_,
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
        return f"{self.name_} [{self.slug.upper()}] {self.now_()}.{config.VIDEO_EXT}"

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
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/114.0.5735.99 Mobile/15E148 Safari/604.1"

        args = [
            "ffmpeg",
            "-hide_banner",
            "-progress",
            "pipe:1",
            "-user_agent",
            ua,
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
