import asyncio
import re
from datetime import datetime

from stardust.apps.chaturbate.db_query import query_bio
from stardust.apps.chaturbate.db_write import (
    write_api_data,
    write_m3u8,
    write_videocontext_fail,
)
from stardust.apps.chaturbate.handleurls import NetActions
from stardust.config.constants import ChatVideoContext, FailVideoContext
from stardust.utils.applogging import HelioLogger, loglvl
from stardust.utils.general import process_hls
from stardust.utils.timer import AppTimer

log = HelioLogger()
processed: list[str] = []


@AppTimer
async def manage_api_videocontext(streamers: list[str]):
    cb_api = NetActions()
    results = await cb_api.get_all_bio(streamers)

    accessible = [data for data in results if isinstance(data, ChatVideoContext)]
    fail = [data for data in results if isinstance(data, FailVideoContext)]

    if accessible:
        has_hls = handle_response(accessible)
        hls_urls = await cb_api.get_all_m3u8(has_hls)
        streamer_url = process_hls(hls_urls)
        write_m3u8(streamer_url)

    if fail:
        write_videocontext_fail(fail)

    log.app(loglvl.SUCCESS, f"Completed {len(accessible)} of {len(streamers)} queries")
    return len(accessible) + len(fail)


def handle_response(results):
    full_json, has_hls = process_response(results)

    profile_data = process_json(full_json)
    write_api_data(profile_data)

    return has_hls


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
    last_broadcast = None

    for js in json_:
        hashtags = handle_hashtags(js.room_title)
        if js.room_status != "public":
            last_broadcast = datetime.today().replace(microsecond=0)
        processed.append(js.broadcaster_username)
        sql_data.append(
            (
                js.broadcaster_username,
                js.age,
                last_broadcast,
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

    names = ["sanda_red"]
    if len(names) == 0:
        return None

    streamers_online = await manage_api_videocontext(names)

    api_fail = [item for item in names if item not in processed]

    log.app(loglvl.SUCCESS, f"{len(api_fail)} of {len(names)} queries")
    if not streamers_online:
        return None

    return streamers_online


if __name__ == "__main__":
    asyncio.run(videocontext())
