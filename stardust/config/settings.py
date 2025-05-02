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


# class HelioSettings(BaseSettings):
APP_NAME: str = "stardust"
APP_DIR: Path = Path.cwd() / APP_NAME


class DBSettings(BaseSettings):
    DB_SQL_FOLDER: Path = APP_DIR / "database"
    DB_FOLDER: Path = APP_DIR / "database" / "db"
    CS_CONFIG: Path = DB_SQL_FOLDER / "camsoda.sql"
    CS_DB_FOLDER: Path = DB_FOLDER / "camsoda.sqlite3"
    CB_CONFIG: Path = DB_SQL_FOLDER / "chaturbate.sql"
    CB_DB_FOLDER: Path = DB_FOLDER / "chaturbate.sqlite3"
    MFC_CONFIG: Path = DB_SQL_FOLDER / "myfreecams.sql"
    MFC_DB_FOLDER: Path = DB_FOLDER / "myfreecams.sqlite3"
    SC_CONFIG: Path = DB_SQL_FOLDER / "stripchat.sql"
    SC_DB_FOLDER: Path = DB_FOLDER / "stripchat.sqlite3"

    DB_SQLS: list[Path] = [CS_CONFIG, CB_CONFIG, MFC_CONFIG, SC_CONFIG]
    DB_FILES: list[Path] = [CS_DB_FOLDER, CB_DB_FOLDER, MFC_DB_FOLDER, SC_DB_FOLDER]


class Settings(BaseSettings):
    BROWSER_PATH: str = "/usr/bin/google-chrome-stable"
    BROWSER_PROFILE: str = str(Path(APP_DIR, "browser/profile"))
    CLI_PROMPT: str = "$"
    COOKIE_DIR: Path = APP_DIR / "browser/app_cookies/"
    COOKIE_CB_NAME: str = "cb_browser_cookies.py"
    COOKIE_CB_PATH: Path = COOKIE_DIR / COOKIE_CB_NAME
    DIR_SSD: Path = Path(f"{env.get('SSD_PATH', f'{APP_DIR}/helio')}")
    DIR_IMG_PATH: Path = Path(f"{env.get('SSD_PATH', f'{APP_DIR}/helio/images')}")
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


def dir_contactsheet(app_name):
    contactsheet= Path(APP_DIR / 'video' / app_name / 'contactsheet')
    location = Path(f"{env.get('SSD_PATH', contactsheet)}")
    return location

@lru_cache(maxsize=None)
def get_setting(**kwargs) -> Settings:
    return Settings(**kwargs)


@lru_cache(maxsize=None)
def get_db_setting(**kwargs) -> DBSettings:
    return DBSettings(**kwargs)
