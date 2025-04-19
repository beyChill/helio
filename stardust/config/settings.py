from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import dotenv_values

# def root_project_folder() -> Path:
#     current_dir = Path(__file__)
#     project_dir = [
#         path_ for path_ in current_dir.parents if path_.parts[-1] == "acecap"
#     ][0]
#     return project_dir

env = dotenv_values("./stardust/.env")


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
    DIR_VIDEO_PATH: Path = Path(DIR_SSD / "videos")
    DIR_VIDEO_REVIEW: Path = Path(
        f"{env.get('DIR_VIDEO_REVIEW', f'{APP_DIR}/video_review')}"
    )
    DIR_VIDEO_SHORT: Path = Path(
        f"{env.get('DIR_VIDEO_SHORT', f'{APP_DIR}/video_short')}"
    )
    DIR_SELENIUM_PROFILE: Path = APP_DIR / "browser/user_profile"
    DIR_PROCESS_CONTACTSHEET: Path = Path(
        f"{env.get('DIR_PROCESS_CONTACTSHEET', f'{APP_DIR}/video_contactsheet')}"
    )
    FFMPEG_DEGUB:bool = False
    VIDEO_EXT:str='mkv'
    VIDEO_LENGTH_SECONDS: int = 1800



@lru_cache(maxsize=None)
def get_setting(**kwargs) -> Settings:
    return Settings(**kwargs)
