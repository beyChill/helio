from datetime import datetime, timedelta
from random import uniform
from typing import Any

import m3u8
from stardust.apps.chaturbate.db_write import write_cb_url
from stardust.utils.applogging import AppLogger
# from stardust.utils.applogging import AppLogger

log = AppLogger()


def script_delay(min: float, max: float):
    delay = uniform(min, max)
    t1 = datetime.now() + timedelta(seconds=delay)
    time_ = datetime.strftime(t1, "%H:%M:%S")

    return (delay, time_)


def process_hls(results: list[Any]):
    streamer_url: list[tuple[str, str]] = []

    for url_, m3u8_ in results:
        m3u8_file = m3u8.loads(m3u8_)

        if not m3u8_file.playlists[-1]:
            continue

        best_quality = m3u8_file.playlists[-1].uri
        new_url = url_.replace("playlist.m3u8", str(best_quality))
        streamer_name = new_url.split("amlst:")[-1].split("-sd-")[0]
        streamer_url.append((streamer_name, new_url))
        write_data = [(v, k) for k, v in streamer_url]
        write_cb_url(write_data)

    return streamer_url
