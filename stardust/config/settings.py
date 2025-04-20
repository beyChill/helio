from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import dotenv_values, find_dotenv

find_env = find_dotenv(".env")
env = dotenv_values(find_env)


def _storage(vid_type: str):
    loc = {"long": env.get("DIR_STORAGE_LOCATIONS"), "keep": env.get("DIR_KEEP_VIDEOS")}
    locations = loc.get(vid_type)
    storage: list[Path] = [Path()]
    if locations:
        # path from .env is string requiring converstion to list[str]
        storage = [Path(loc) for loc in locations.split(",")]
    return storage


class Settings(BaseSettings):
    APP_NAME: str = "stardust"
    APP_DIR: Path = Path.cwd() / APP_NAME
    BROWSER_PATH: str = "/usr/bin/google-chrome-stable"
    BROWSER_PROFILE: str = str(Path(APP_DIR, "browser/profile"))
    CLI_PROMPT: str = "$"
    COOKIE_DIR: Path = APP_DIR / "browser/app_cookies/"
    COOKIE_CB_NAME: str = "cb_browser_cookies.py"
    COOKIE_CB_PATH: Path = COOKIE_DIR / COOKIE_CB_NAME
    DB_CONFIG: Path = APP_DIR / "database/dbconfig.sql"
    DB_NAME: str = f"{APP_NAME}.sqlite3"
    DB_FOLDER: Path = APP_DIR / "database" / "db"
    DB_PATH: Path = DB_FOLDER / DB_NAME
    DIR_SSD: Path = Path(f"{env.get('SSD_PATH', f'{APP_DIR}/videos')}")
    DIR_IMG_PATH: Path = Path(f"{env.get('SSD_PATH', f'{APP_DIR}/images')}")
    DIR_PROCESS_CONTACTSHEET: Path = Path(
        f"{env.get('DIR_PROCESS_CONTACTSHEET', f'{APP_DIR}/video_contactsheet')}"
    )
    DIR_SELENIUM_PROFILE: Path = APP_DIR / "browser/user_profile"
    DIR_VIDEO_PATH: Path = Path(DIR_SSD / "videos")
    DIR_VIDEO_REVIEW: Path = Path(
        f"{env.get('DIR_VIDEO_REVIEW', f'{APP_DIR}/video_review')}"
    )
    DIR_VIDEO_SHORT: Path = Path(
        f"{env.get('DIR_VIDEO_SHORT', f'{APP_DIR}/video_short')}"
    )
    FFMPEG_DEGUB: bool = False
    VIDEO_EXT: str = "mkv"
    VIDEO_LENGTH_SECONDS: int = 1800
    LOCAL_STORAGE: list[Path] = _storage("long")
    LOCAL_STORAGE.append(DIR_VIDEO_PATH)
    DIR_STORAGE_LOCATIONS: list[Path] = LOCAL_STORAGE
    DIR_KEEP_PATH: Path = Path(f"{APP_DIR}/video_keep")
    KEEP_STORAGE: list[Path] = _storage("keep")
    KEEP_STORAGE.append(DIR_KEEP_PATH)
    DIR_KEEP_VIDEOS: list[Path] = KEEP_STORAGE


@lru_cache(maxsize=None)
def get_setting(**kwargs) -> Settings:
    return Settings(**kwargs)
