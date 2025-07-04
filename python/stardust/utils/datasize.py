import os
from itertools import groupby
from operator import itemgetter

from stardust.apps.manage_app_db import HelioDB
from stardust.config.settings import get_setting
from stardust.utils.general import calc_size
from stardust.utils.timer import AppTimerSync


@AppTimerSync
def find_size_review():
    DIRS = get_setting().DIR_STORAGE_LOCATIONS
    data = [
        (file.name.split(" ")[0], file) for dir in DIRS for file in dir.rglob("*.m*")
    ]
    return calculations(data)


@AppTimerSync
def find_size_keep():
    DIRS = get_setting().DIR_KEEP_VIDEOS
    data = [
        (file.name.split(" ")[0], file) for dir in DIRS for file in dir.rglob("*.m*")
    ]
    return calculations(data)


def calculations(data):
    total_size = []
    results: list[tuple[str, float]] = []
    streamer: str = ""
    data.sort(key=itemgetter(0))
    grouped = [list(group) for _, group in groupby(data, key=itemgetter(0))]
    for folder in grouped:
        for file in folder:
            streamer, video = file
            total_size.append(os.stat(video).st_size)

        gigabyte = calc_size(total_size)
        total_size = []
        results.append((streamer, gigabyte))
    return results


def get_video_sizes():
    storage_ = find_size_review()
    keep = find_size_keep()
    HelioDB().write_data_review(storage_)
    HelioDB().write_data_keep(keep)


if __name__ == "__main__":
    get_video_sizes()