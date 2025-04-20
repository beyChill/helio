from pathlib import Path

# from database.dbconnections import db_init
from config.settings import get_setting
from utils.applogging import HelioLogger, loglvl

log = HelioLogger()


def create_init_folders():
    dir_ = get_setting()

    dirs = [
        dir_.COOKIE_DIR,
        dir_.DB_FOLDER,
        dir_.DIR_PROCESS_CONTACTSHEET,
        dir_.DIR_SELENIUM_PROFILE,
        dir_.DIR_VIDEO_SHORT,
        dir_.DIR_VIDEO_REVIEW,
        dir_.DIR_KEEP_PATH
    ]

    _ = [create_folder(path_) for path_ in dirs if not path_.exists()]


def create_folder(folder: Path):
    log.info("Creating app directories")
    folder.mkdir(parents=True, exist_ok=True)
    log.app(loglvl.CREATED, f"{folder.name} folder...")
    print(" " * 2, str(folder))


# @AppTimer()
def main():
    create_init_folders()


if __name__ == "__main__":
    main()
