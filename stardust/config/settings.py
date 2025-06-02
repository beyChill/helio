from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values, find_dotenv
from pydantic_settings import BaseSettings

find_env = find_dotenv(".env")
env = dotenv_values(find_env)


class MitmProxyDirs:
    def __init__(self):
        self.parent = ".helio"
        self.base = self._find_base_dir()
        self.conf = self.create_config()
        self.data = self.create_data()

    def _find_base_dir(self):
        home = Path("~/")
        base = Path.expanduser(home)
        return base

    def create_config(self):
        conf = Path(self.base / self.parent / "mitmproxy")
        conf.mkdir(parents=True, exist_ok=True)
        return conf

    def create_data(self):
        data = Path(self.base / self.parent / "data")
        data.mkdir(parents=True, exist_ok=True)
        return data


def _storage(vid_type: str):
    loc = {"long": env.get("DIR_STORAGE_LOCATIONS"), "keep": env.get("DIR_KEEP_VIDEOS")}
    locations = loc.get(vid_type)
    storage: list[Path] = [Path()]
    if locations:
        # path from .env is string requiring converstion to list[str]
        storage = [Path(loc) for loc in locations.split(",")]
    return storage


# class HelioSettings(BaseSettings):
APP_NAME: str = "stardust"
APP_DIR: Path = Path.cwd() / APP_NAME


class DBSettings(BaseSettings):
    DB_SQL_FOLDER: Path = APP_DIR / "database"
    CS_CONFIG: Path = DB_SQL_FOLDER / "camsoda.sql"
    CB_CONFIG: Path = DB_SQL_FOLDER / "chaturbate.sql"
    MFC_CONFIG: Path = DB_SQL_FOLDER / "myfreecams.sql"
    SC_CONFIG: Path = DB_SQL_FOLDER / "stripchat.sql"

    DB_SQLS: list[Path] = [CS_CONFIG, CB_CONFIG, MFC_CONFIG, SC_CONFIG]


class Settings(BaseSettings):
    BROWSER_PATH: str = "/usr/bin/google-chrome-stable"
    BROWSER_PROFILE: str = str(Path(APP_DIR, "browser/profile"))
    CLI_PROMPT: str = "$"
    COOKIE_DIR: Path = APP_DIR / "browser/app_cookies/"
    COOKIE_CB_NAME: str = "cb_browser_cookies.py"
    COOKIE_CB_PATH: Path = COOKIE_DIR / COOKIE_CB_NAME
    DIR_SSD: Path = Path(f"{env.get('SSD_PATH', f'{APP_DIR}/helio')}")
    DIR_SELENIUM_PROFILE: Path = APP_DIR / "browser/user_profile"
    DIR_IMG_PATH: Path = Path(
        f"{env.get('SSD_PATH_IMAGES', f'{APP_DIR}/capture/images')}"
    )
    DIR_PROCESS_CONTACTSHEET: Path = Path(
        f"{env.get('DIR_PROCESS_CONTACTSHEET', f'{APP_DIR}/capture/video_contactsheet')}"
    )
    DIR_VIDEO_PATH: Path = Path(
        f"{env.get('SSD_PATH_VIDEOS', f'{APP_DIR}/capture/videos')}"
    )
    DIR_VIDEO_REVIEW: Path = Path(
        f"{env.get('DIR_VIDEO_REVIEW', f'{APP_DIR}/capture/video_review')}"
    )
    DIR_VIDEO_SHORT: Path = Path(
        f"{env.get('DIR_VIDEO_SHORT', f'{APP_DIR}/capture/video_short')}"
    )
    DIR_KEEP_PATH: Path = Path(f"{APP_DIR}/capture/video_keep")
    DIR_MITM_CONFIG: Path = MitmProxyDirs().create_config()
    DIR_MITM_DATA: Path = MitmProxyDirs().create_data()
    FFMPEG_DEGUB: bool = False
    VIDEO_EXT: str = "mkv"
    VIDEO_LENGTH_SECONDS: int = 1800
    LOCAL_STORAGE: list[Path] = _storage("long")
    LOCAL_STORAGE.append(DIR_VIDEO_PATH)
    DIR_STORAGE_LOCATIONS: list[Path] = LOCAL_STORAGE
    KEEP_STORAGE: list[Path] = _storage("keep")
    KEEP_STORAGE.append(DIR_KEEP_PATH)
    DIR_KEEP_VIDEOS: list[Path] = KEEP_STORAGE
    DIR_HASH_REF: Path = APP_DIR / "apps" / "myfreecams" / "assets" / "hash"


@lru_cache(maxsize=None)
def get_setting(**kwargs) -> Settings:
    return Settings(**kwargs)


@lru_cache(maxsize=None)
def get_db_setting(**kwargs) -> DBSettings:
    return DBSettings(**kwargs)
