import asyncio
from pathlib import Path

from rnet import Response

import stardust.utils.heliologger as log
from stardust.apps.chaturbate.handleurls import iNetCb
from stardust.apps.manage_app_db import HelioDB
from stardust.apps.manage_capture import start_capture
from stardust.utils.general import make_image_dir, script_delay
from stardust.utils.handle_m3u8 import HandleM3u8
from stardust.utils.timer import AppTimer

APP_SITE = "chaturbate"
iNet = iNetCb()


@AppTimer
async def get_online_cb_streamers():
    db = HelioDB(slug="CB")
    if not (streamers := db.query_site_streamers()):
        log.warning("Zero Chaturbate streamers to capture")
        return []

    if not (results := await check_online_status(streamers)):
        log.query(f"0 of {len(streamers)} Chaurbate streamers online")
        return []

    online = process_results(results)
    urls = await iNet.get_ajax_url(online)

    urls_ = {url["url"] for url in urls}

    all_url = {await HandleM3u8(url).cb_m3u8() for url in urls_}

    streamer_url = {x for x in all_url if x is not None}

    online_data = {(name_, "cb", url) for url, name_, *_ in streamer_url}

    return online_data


async def check_online_status(streamers: set[str]):
    data = await iNet.get_all_jpg(streamers)

    results = [(response, image) for response, image in data if image]

    return results


def process_results(results: list[tuple[Response, bytes]]):
    online_streamers: list[str] = []
    for streamer in results:
        response, image = streamer
        name_ = response.url.split("=")[-1]
        img_dir = make_image_dir(name_, APP_SITE)
        download_img(image, name_, img_dir)
        online_streamers.append(name_)

    return online_streamers


def download_img(streamer, name_: str, img_dir: Path):
    download_image = Path(img_dir, f"{name_}.jpg").joinpath()
    download_image.write_bytes(streamer)


async def manage_seek_capture():
    while True:
        online_streamers = await get_online_cb_streamers()

        if online_streamers:
            start_capture(online_streamers)

        delay_, time_ = script_delay(249.07, 395.89)

        log.query(f"CB streamers for capture @: {time_}")

        await asyncio.sleep(delay_)


def loop_cb_seek_capture():
    loop = asyncio.new_event_loop()
    loop.create_task(manage_seek_capture())
    loop.run_forever()


if __name__ == "__main__":
    loop_cb_seek_capture()
