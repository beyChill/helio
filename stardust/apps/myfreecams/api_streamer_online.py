import asyncio
import random
from threading import Thread

from stardust.apps.manage_app_db import HelioDB
from stardust.apps.manage_capture import start_capture
from stardust.apps.myfreecams.api_get_jsons import mitm_init
from stardust.apps.myfreecams.db_myfreemcams import DbMfc
from stardust.apps.myfreecams.handleurls import iNetMfc
from stardust.apps.myfreecams.helper import mfc_server_offset
from stardust.utils.applogging import HelioLogger
from stardust.utils.general import script_delay
from stardust.utils.handle_m3u8 import HandleM3u8

log = HelioLogger()
iNet = iNetMfc()
db = HelioDB(slug="MFC")


async def get_online_streamers():
    """An api request providing minimal data
    Relevant data is the streamer's username
    """
    response = await iNet.get_tagged_streamers()
    data = response.result.data

    return {streamer.username for streamer in data}


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
    m3u8 = []
    streamer_data = []
    for name_, url in playlist:
        uri = await HandleM3u8(url).mfc_m3u8()
        m3u8.append((uri, name_, "MFC"))
        streamer_data.append((name_, "MFC", uri))

    return (m3u8, streamer_data)


async def delay_():
    delay_, time_ = script_delay(300.07, 366.89)
    log.info(f"Next MFC streamer query: {time_}")
    await asyncio.sleep(delay_)


async def manage_seek_capture():
    while True:
        if not (seek_capture := db.query_site_streamers()):
            log.warning("Zero MFC streamers to capture")
            await delay_()
            continue

        online_streamers = await get_online_streamers()
        capture_streamers = seek_capture.intersection(online_streamers)

        if len(capture_streamers) == 0:
            await delay_()
            continue
        # returns streamers having an update within past 6 minutes
        m3u8_data = DbMfc("myfreecams").query_m3u8_data(capture_streamers)

        # difference means the data in the table is probably outdated
        if len(capture_streamers) != len(m3u8_data):
            # Update database with recent data for streamers
            # mitmproxy need
            thread = Thread(target=mitm_init, daemon=True)
            thread.start()
            thread.join()

            # 2nd attempt to attain data to build the m3u8 playlist
            m3u8_data = DbMfc("myfreecams").query_m3u8_data(capture_streamers)

        playlist = build_m3u8s(m3u8_data)
        m3u8s, streamer_data = await organize_capture_data(playlist)

        start_capture(streamer_data)
        db.write_capture_url(m3u8s)

        await delay_()


def loop_mfc_seek_capture():
    loop = asyncio.new_event_loop()
    loop.create_task(manage_seek_capture())
    loop.run_forever()


if __name__ == "__main__":
    loop_mfc_seek_capture()
