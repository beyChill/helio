from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values, find_dotenv
from pydantic_settings import BaseSettings

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
SAVE_ROOT_DIR:Path = Path.cwd()
APP_DIR: Path = SAVE_ROOT_DIR / "python" / APP_NAME

print(APP_DIR)
class DBSettings(BaseSettings):
    DB_SQL_FOLDER: Path = APP_DIR / "database"
    CS_CONFIG: Path = DB_SQL_FOLDER / "camsoda.sql"
    CB_CONFIG: Path = DB_SQL_FOLDER / "chaturbate.sql"
    MFC_CONFIG: Path = DB_SQL_FOLDER / "myfreecams.sql"
    SC_CONFIG: Path = DB_SQL_FOLDER / "stripchat.sql"

    DB_SQLS: list[Path] = [CS_CONFIG, CB_CONFIG, MFC_CONFIG, SC_CONFIG]


class Settings(BaseSettings):
    CLI_PROMPT: str = "$"
    DIR_SSD: Path = Path(f"{env.get('SSD_PATH', f'{APP_DIR}/helio')}")
    DIR_IMG_PATH: Path = Path(
        f"{env.get('SSD_PATH_IMAGES', f'{SAVE_ROOT_DIR}/capture/images')}"
    )
    DIR_KEEP_PATH: Path = Path(f"{SAVE_ROOT_DIR}/capture/video_keep")
    DIR_VIDEO_PATH: Path = Path(
        f"{env.get('SSD_PATH_VIDEOS', f'{SAVE_ROOT_DIR}/capture/videos')}"
    )
    DIR_VIDEO_REVIEW: Path = Path(
        f"{env.get('DIR_VIDEO_REVIEW', f'{SAVE_ROOT_DIR}/capture/video_review')}"
    )
    DIR_VIDEO_SHORT: Path = Path(
        f"{env.get('DIR_VIDEO_SHORT', f'{SAVE_ROOT_DIR}/capture/video_short')}"
    )
    FFMPEG_STDOUT: bool = False
    VIDEO_EXT: str = "mkv"
    VIDEO_MAX_SECONDS: int = 1800
    VIDEO_LENGTH_OVERLAP: int = 15
    LOCAL_STORAGE: list[Path] = _storage("long")
    LOCAL_STORAGE.append(DIR_VIDEO_PATH)
    DIR_STORAGE_LOCATIONS: list[Path] = LOCAL_STORAGE
    KEEP_STORAGE: list[Path] = _storage("keep")
    KEEP_STORAGE.append(DIR_KEEP_PATH)
    DIR_KEEP_VIDEOS: list[Path] = KEEP_STORAGE
    # DIR_HASH_REF: Path = APP_DIR / "apps" / "myfreecams" / "assets" / "hash"


@lru_cache(maxsize=None)
def get_setting(**kwargs) -> Settings:
    return Settings(**kwargs)


@lru_cache(maxsize=None)
def get_db_setting(**kwargs) -> DBSettings:
    return DBSettings(**kwargs)
