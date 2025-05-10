import asyncio
import re
from datetime import datetime

from stardust.apps.chaturbate.db_chaturbate import DbCb
from stardust.apps.chaturbate.handleurls import NetActions
from stardust.apps.chaturbate.models import ChatVideoContext, FailVideoContext
from stardust.utils.applogging import HelioLogger, loglvl
from stardust.utils.handle_m3u8 import HandleM3u8
from stardust.utils.timer import AppTimer

log = HelioLogger()
processed: list[str] = []
db = DbCb("chaturbate")

iNet = NetActions()


@AppTimer
async def query_api_videocontext(streamers: list[str]):
    results = await iNet.get_all_bio(streamers)

    return results


async def handle_results(results: list[FailVideoContext | ChatVideoContext]):
    success = {data for data in results if isinstance(data, ChatVideoContext)}

    fail = {data for data in results if isinstance(data, FailVideoContext)}

    if not success:
        log.error("Chaturbate calls to videocontext api failed")
        return None

    if fail:
        db.write_videocontext_fail(fail)
        return None

    profile_data = process_json(success)
    db.write_api_data(profile_data)
    has_m3u8 = chk_m3u8(success)

    streamers_online = [
        (HandleM3u8(url).new_cb_m3u8(), name_) for name_, url in has_m3u8
    ]

    db.write_capture_url(streamers_online)

    log.debug(
        f"Success: {len(success)} / fail: {len(fail)} || {len(results)} CB api videocontext queries"
    )
    return streamers_online


def chk_m3u8(results: set[ChatVideoContext]):
    hls_url = {
        (result.broadcaster_username, result.hls_source)
        for result in results
        if result.hls_source
    }

    return hls_url


def process_json(json_: set[ChatVideoContext]):
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


async def manage_api_query():
    if not (streamers := db.query_bio()):
        log.warning("Zero CB steamers need bio update")
        return None

    names = [streamer[0] for streamer in streamers]

    if len(names) == 0:
        return None

    results = await query_api_videocontext(names)
    streamers_online = await handle_results(results)
    api_fail = [item for item in names if item not in processed]

    log.app(loglvl.SUCCESS, f"{len(streamers) - len(api_fail)} of {len(names)} queries")
    if not streamers_online:
        return None

    return streamers_online


if __name__ == "__main__":
    asyncio.run(manage_api_query())
