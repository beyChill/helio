import os
from itertools import groupby
from operator import itemgetter

from stardust.apps.chaturbate.db_write import write_data_keep, write_data_review
from stardust.config.settings import get_setting
from stardust.utils.general import calc_size
from stardust.utils.timer import AppTimerSync


@AppTimerSync
def size_storage():
    DIRS = get_setting().DIR_STORAGE_LOCATIONS
    data = [
        (file.name.split(" ")[0], file) for dir in DIRS for file in dir.rglob("*.m*")
    ]
    results = calculations(data)
    return results


@AppTimerSync
def size_keep():
    DIRS = get_setting().DIR_KEEP_VIDEOS
    data = [
        (file.name.split(" ")[0], file) for dir in DIRS for file in dir.rglob("*.m*")
    ]
    results = calculations(data)
    return results


def calculations(data):
    total_size = []
    results = []
    streamer = ""
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
    storage_ = size_storage()
    keep = size_keep()
    write_data_review(storage_)
    write_data_keep(keep)


if __name__ == "__main__":
    get_video_sizes()
