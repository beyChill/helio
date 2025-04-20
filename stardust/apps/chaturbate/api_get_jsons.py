from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from random import uniform
from sqlite3 import Date

from stardust.apps.chaturbate.db_write import write_db_streamers
from stardust.apps.chaturbate.handleurls import NetActions
from stardust.config.constants import CBRoom, cb_param
from stardust.utils.applogging import HelioLogger
from stardust.utils.timer import AppTimer

log = HelioLogger(debug=True)


def url_param(category=cb_param.FEMALE, tag=cb_param.TAG.NONE):
    cat = category
    subcat = tag.value

    parameter = cat

    if parameter == "?":
        return parameter

    if subcat:
        parameter = f"{parameter}&{subcat}"
    return parameter


@AppTimer
async def get_streamers_online():
    """download and process json files for a predefined category (url_params) of streamers"""
    iNet = NetActions()

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
        location = None if val.location == "" else val.location
        country = None if val.country == "" else val.country
        is_new = None if not val.is_new else "NEW"
        tags = None if not val.tags else " ".join(val.tags)
        bio_date = Date.today()

        values.append(
            (name_, age, last, follow, view, location, country, is_new, tags, bio_date)
        )

    return values


async def manage_cb_room_list():
    while True:
        json_data = await get_streamers_online()
        if json_data is not None:
            db_data = prep_db_entries(json_data)
            write_db_streamers(db_data)
        log.info(f"{len(json_data)} chaturbate steamers online")
        # Delay reduces api queries per timeframe
        delay_ = set_script_delay()
        await asyncio.sleep(delay_)


def set_script_delay():
    # A random delay between min, max in seconds
    # used to slow script execution
    delay_ = uniform(671.05, 1088.47)
    t1 = datetime.now() + timedelta(seconds=delay_)
    log.info(f"Next CB streamer filtered query: {datetime.strftime(t1, '%H:%M:%S')}")
    return delay_


def exception_handler(loop, context) -> None:
    log.error(context["exception"])
    log.error(context["message"])


def loop_cb_room_list():
    loop = asyncio.new_event_loop()
    loop.set_exception_handler(exception_handler)
    loop.create_task(manage_cb_room_list())
    loop.run_forever()


if __name__ == "__main__":
    loop_cb_room_list()
