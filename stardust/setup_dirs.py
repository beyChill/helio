from pathlib import Path

from config.settings import get_setting
from config.log_display_setting import log_permissions_init
import stardust.utils.heliologger as log


def create_init_folders():
    dir_ = get_setting()

    dirs = [
        dir_.COOKIE_DIR,
        dir_.DIR_PROCESS_CONTACTSHEET,
        dir_.DIR_SELENIUM_PROFILE,
        dir_.DIR_VIDEO_SHORT,
        dir_.DIR_VIDEO_REVIEW,
        dir_.DIR_KEEP_PATH,
        dir_.DIR_MITM_CONFIG,
        dir_.DIR_MITM_DATA,
    ]

    _ = [create_folder(path_) for path_ in dirs if not path_.exists()]


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
