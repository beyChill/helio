import asyncio
from pathlib import Path

from rnet import Response

from stardust.apps.chaturbate.db_query import query_seek_status
from stardust.apps.chaturbate.handleurls import NetActions
from stardust.apps.chaturbate.manage_capture import start_capture
from stardust.utils.applogging import HelioLogger
from stardust.utils.general import process_cb_hls, script_delay
from stardust.utils.timer import AppTimer

log = HelioLogger()
iNet = NetActions()


@AppTimer
async def get_streamers():
    data = query_seek_status()

    if not data:
        log.warning("Zero Chaturbate streams to capture")
        return []

    streamers = [name_ for (name_,) in data]

    if not (results := await check_online_status(streamers)):
        log.info(f"0 of {len(data)} Chaurbate streamers online")
        return []

    online = process_results(results)
    urls = await iNet.get_ajax_url(online)

    urls_ = [url["url"] for url in urls]
    hls_urls = await iNet.get_all_m3u8(urls_)

    streamer_url = process_cb_hls(hls_urls)

    return streamer_url


async def check_online_status(streamers: list[str]):
    data = await iNet.get_all_jpg(streamers)

    results = [(response, image) for response, image in data if image]

    return results


def process_results(results: list[tuple[Response, bytes]]):
    online_streamers: list[str] = []
    for streamer in results:
        response, image = streamer
        name_ = response.url.split("=")[-1]
        img_dir = make_image_dir(name_)
        download_img(image, name_, img_dir)
        online_streamers.append(name_)

    return online_streamers


def make_image_dir(name_: str) -> Path:
    img_path = Path("/mnt/Alpha/_bey/uv/aaacapture/app/webactions")
    dir_name = list(name_)
    dir_name_upper = dir_name[0].upper()
    path_ = Path(img_path / "chaturbate", dir_name_upper).joinpath()

    if not path_.exists():
        path_.mkdir(parents=True, exist_ok=True)

    return path_


def download_img(streamer, name_: str, img_dir: Path):
    download_image = Path(img_dir, f"{name_}.jpg").joinpath()
    download_image.write_bytes(streamer)


async def manage_online_status():
    while True:
        online_streamers = await get_streamers()

        if online_streamers:
            start_capture(online_streamers)

        delay_, time_ = script_delay(209.07, 395.89)

        log.info(f"Seek CB streamers: {time_}")
        await asyncio.sleep(delay_)


def run_cb_streamers():
    loop = asyncio.new_event_loop()
    loop.create_task(manage_online_status())
    loop.run_forever()


if __name__ == "__main__":
    run_cb_streamers()
