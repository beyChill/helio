import asyncio
from datetime import datetime
import re

from stardust.apps.chaturbate.handleurls import CbUrls
from stardust.apps.chaturbate.db_query import query_bio
from stardust.apps.chaturbate.db_write import write_cb_api_data, write_cb_url
from stardust.config.constants import ChatVideoContext
from stardust.config.settings import get_setting
from stardust.utils.applogging import HelioLogger, loglvl
from stardust.utils.general import process_hls
from stardust.utils.timer import AppTimer

log = HelioLogger()


@AppTimer
async def manage_api_videocontext(streamers: list[str]):
    cb_api = CbUrls()
    results = await cb_api.get_all_bio(streamers)

    full_json, has_hls = process_response(results)

    # if not has_hls:
    #     return None

    profile_data = process_json(full_json)
    write_cb_api_data(profile_data)

    hls_urls = await cb_api.get_all_m3u8(has_hls)
    streamer_url = process_hls(hls_urls)
    write_cb_url(streamer_url)

    log.app(
        loglvl.SUCCESS, f"Completed {len(streamer_url)} of {len(streamers)} queries"
    )
    return streamer_url


def process_response(results):
    full_json = []
    hls_url: list[str] = []
    for result in results:
        full_json.append(ChatVideoContext(**result))
        if result["hls_source"]:
            hls_url.append(result["hls_source"])

    return full_json, hls_url


def process_json(json_: list[ChatVideoContext]):
    sql_data = []

    for js in json_:
        hashtags = handle_hashtags(js.room_title)
        if js.room_status == "public":
            sql_data.append(
                (
                    js.broadcaster_username,
                    js.age,
                    datetime.today().replace(microsecond=0),
                    js.num_viewers,
                    hashtags,
                )
            )

    return sql_data


def handle_hashtags(text: str):
    hashtags: list[str] = []
    hashtag_to_str = ""
    regex = "#(\\w+)"

    hashtag_list = re.findall(regex, text)

    for hashtag in hashtag_list:
        hashtags.append(hashtag)
        hashtag_to_str = " ".join(hashtags)

    return hashtag_to_str


async def videocontext():
    streamers = query_bio()
    names = [streamer[0] for streamer in streamers]

    if len(names) == 0:
        return None

    streamers_online = await manage_api_videocontext(names)

    if not streamers_online:
        return None

    return streamers_online


if __name__ == "__main__":
    asyncio.run(videocontext())
