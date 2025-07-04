from pathlib import Path

from stardust.config.log_display_setting import log_permissions_init
from stardust.config.settings import get_setting
import stardust.utils.heliologger as log


def create_init_folders():
    dir_ = get_setting()

    dirs = [
        dir_.DIR_IMG_PATH,
        dir_.DIR_KEEP_PATH,
        dir_.DIR_VIDEO_PATH,
        dir_.DIR_VIDEO_REVIEW,
        dir_.DIR_VIDEO_SHORT,
    ]

    _ = [create_folder(path_) for path_ in dirs]


def create_folder(folder: Path):
    log.info("Creating app directories")
    folder.mkdir(parents=True, exist_ok=True)
    log.created(f"{folder.name} folder...")
    log.created(str(folder))


def main():
    log_permissions_init()
    create_init_folders()


if __name__ == "__main__":
    main()
