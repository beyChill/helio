# Get api data for all online streamers
# save data to sqlite database

from __future__ import annotations

import asyncio
from datetime import datetime
from sqlite3 import Date

import stardust.utils.heliologger as log
from stardust.apps.chaturbate.db_chaturbate import DbCb
from stardust.apps.chaturbate.handleurls import iNetCb
from stardust.apps.chaturbate.models import CBRoom, cb_param
from stardust.utils.general import script_delay
from stardust.utils.timer import AppTimer


def url_param(category=cb_param.FEMALE, tag=cb_param.TAG.NONE):
    if category == "?":
        return category

    if tag.value:
        category = f"{category}&{tag.value}"

    return category


@AppTimer
async def get_streamers_online():
    """download and process json files for a predefined category (url_params) of streamers"""
    iNet = iNetCb()

    params = url_param(cb_param.FEMALE, cb_param.TAG.NONE)

    # the first call to 'get_all_jsons' obtains total online streamers.
    # The total is used to calculate max urls to generate.
    # Each url has a max capacity of 90 streamers. App generates urls until the
    # all online streamers are accounted for.
    req = await iNet.get_all_jsons(params)
    initial = req[0]

    streamers_online = initial.total_count
    # streamers_online = 180

    results = await iNet.get_all_jsons(params, streamers_online)
    results.append(initial)

    json_data: list[CBRoom] = [
        streamer for streamers in results for streamer in streamers.rooms
    ]

    return json_data


def prep_db_entries(json_data: list[CBRoom]):
    values = []
    today_ = datetime.today().replace(microsecond=0)

    for val in json_data:
        if val.current_show != "public":
            log.warning(val.current_show)
        name_ = val.username
        age = None if val.display_age == "" else val.display_age
        last = today_
        follow = val.num_followers
        view = val.num_users
        start_dt_utc = val.start_dt_utc
        location = None if val.location == "" else val.location
        country = None if val.country == "" else val.country
        is_new = None if not val.is_new else "NEW"
        tags = None if not val.tags else " ".join(val.tags)
        bio_date = Date.today()

        values.append(
            (
                name_,
                age,
                last,
                follow,
                view,
                start_dt_utc,
                location,
                country,
                is_new,
                tags,
                bio_date,
            )
        )

    return values


async def manage_cb_room_list():
    db = DbCb("chaturbate")
    while True:
        json_data = await get_streamers_online()
        if json_data is not None:
            db_data = prep_db_entries(json_data)
            db.write_db_streamers(db_data)
        log.info(f"{len(json_data)} chaturbate steamers online")
        # Delay reduces api queries per timeframe
        delay_, time_ = script_delay(609.07, 1095.89)
        log.query(f"Data for CB streamers @: {time_}")
        await asyncio.sleep(delay_)

def exception_handler(loop, context) -> None:
    log.error(context["exception"])
    log.error(context["message"])


def loop_cb_all_online():
    loop = asyncio.new_event_loop()
    loop.set_exception_handler(exception_handler)
    loop.create_task(manage_cb_room_list())
    loop.run_forever()


if __name__ == "__main__":
    loop_cb_all_online()
