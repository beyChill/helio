import asyncio
import random
import time

import stardust.utils.heliologger as log
from stardust.apps.manage_app_db import HelioDB
from stardust.apps.manage_capture import start_capture
from stardust.apps.myfreecams.db_myfreecams import DbMfc
from stardust.apps.myfreecams.handleurls import iNetMfc
from stardust.apps.myfreecams.helper import mfc_server_offset
from stardust.utils.general import script_delay
from stardust.utils.handle_m3u8 import HandleM3u8

db = HelioDB(slug="MFC")


async def get_online_streamers():
    """An api request providing minimal data.
    Relevant data is the streamer's username.
    Also converts names to lower case to ease 
    comparison.
    """
    iNet = iNetMfc()
    response = await iNet.get_tagged_streamers()
    data = response.result.data

    return {streamer.username.lower() for streamer in data}


def build_m3u8s(data):
    playlist = []

    for name_, cam, phase, pid, uid in data:
        phase_fix = ""
        server = mfc_server_offset(cam)

        if phase == "a":
            phase_fix = "a_"

        pid = str(pid)

        # Eight is mininum number of digits for a url's id
        id = str(uid).zfill(8)

        session_name = "".join([phase_fix, pid, id])

        nc_value = random.random()
        playlist.append(
            (
                name_,
                f"https://edgevideo.myfreecams.com/llhls/NxServer/{server}/ngrp:mfc_{session_name}.f4v_cmaf/playlist.m3u8?nc={nc_value}&v=1.97.23",
            )
        )

    return playlist


async def organize_capture_data(playlist):
    # just changing the sequence for function args
    m3u8 = []
    streamer_data = []
    for name_, url in playlist:
        uri = await HandleM3u8(url).mfc_m3u8()
        m3u8.append((uri, name_, "MFC"))
        streamer_data.append((name_, "MFC", uri))

    return (m3u8, streamer_data)


async def get_online_mfc_streamers():
    if not (seek_capture := db.query_streamers_for_capture()):
        log.warning("Zero MFC streamers to capture")
        return []

    online_streamers = await get_online_streamers()

    capture_streamers = seek_capture.intersection(online_streamers)

    if len(capture_streamers) == 0:
        log.query(f"0 of {len(seek_capture)} MyFreeCams streamers online")
        return []

    # returns streamers having an update within past 6 minutes are most likely online 
    # 6 minutes is within timeframe for fetching new data from api.
    if not (m3u8_data := DbMfc("myfreecams").query_m3u8_data(capture_streamers)):
        return []

    playlist = build_m3u8s(m3u8_data)
    m3u8s, streamer_data = await organize_capture_data(playlist)
    db.write_capture_url(m3u8s)

    return streamer_data


def manage_seek_capture():
    while True:
        online_streamers = asyncio.run(get_online_mfc_streamers())

        if online_streamers:
            start_capture(online_streamers)

        delay_, time_ = script_delay(285.27, 396.89)
        log.query(f"MFC streamers for capture @: {time_}")
        time.sleep(delay_)


def loop_mfc_seek_capture():
    # This script depends on the data from
    # another script (MFC: api_ws_json).
    # Delaying start allows for api call and
    # data acquistion, which takes about
    # a second. Five seconds is a good buffer
    # TODO consider combining the two scripts
    time.sleep(5)
    loop = asyncio.new_event_loop()
    loop.create_task(manage_seek_capture())
    loop.run_forever()


if __name__ == "__main__":
    manage_seek_capture()
