import random

from tabulate import tabulate

import stardust.utils.heliologger as log
from stardust.apps.myfreecams.db_myfreecams import DbMfc
from stardust.apps.myfreecams.json_models import Lookup, LookupSession

def get_name_url(streamer: Lookup):
    name_ = streamer.method.split("/")[-1]
    session = streamer.result.user.sessions[-1]
    streamer_id = streamer.result.user.id
    playlist_url = make_playlist(session, streamer_id)
    return (playlist_url, name_)


def make_playlist(session: LookupSession, streamer_id: int):
    server = mfc_server_offset(session.vidserver_id)

    phase = session.phase

    pid = str(session.platform_id)

    # 8 is mininum number of digits for a url's id
    id = str(streamer_id).zfill(8)

    session_id = "".join([phase, pid, id])

    nc_value = random.random()

    url = f"https://edgevideo.myfreecams.com/llhls/NxServer/{server}/ngrp:mfc_{session_id}.f4v_cmaf/playlist.m3u8?nc={nc_value}&v=1.97.23"
    return url


def mfc_server_offset(server: int):
    if 845 <= server <= 1399:
        return server - 500

    if 1545 <= server <= 1559:
        return server - 1000

    if 1600 <= server <= 1944:
        return server - 700

    if 3000 <= server <= 3040:
        return server - 1000

    raise ValueError("Offset calc for MyFreeCams server failed")


MFC_STREAMER_STATUS = {
    0: "public",
    2: "away",
    12: "private",
    13: "group show",
    14: "club",
    90: "hidden",
    127: "offline",
}


def chk_online_status(streamer: Lookup, name_: str, slug: str):
    try:
        if not streamer.result.user.sessions:
            log.offline(f"{name_} [{slug}]")
            return None

        status = MFC_STREAMER_STATUS.get(
            streamer.result.user.sessions[-1].vstate, "unknown"
        )

        if status != "public":
            if status == "offline":
                log.offline(f"{name_} [{slug}]")
                return None
            log.stopped(f"{name_} [{slug}] is {status}")
            return None

        return streamer
    except Exception as e:
        log.error(e)
        return None


def video_state_table(summary):
    db = DbMfc("myfreecams")
    videostate = db.query_count_recent_videostate()

    # list have sort method.
    summary = [(MFC_STREAMER_STATUS.get(key), int(total)) for key, total in videostate]
    head = [
        "Status",
        "Streamers",
    ]
    print(tabulate(summary, headers=head, tablefmt="pretty", colalign=("left", "left")))

WS_SERVERS=[
"wchat5",
"wchat7",
"wchat8",
"wchat10",
"wchat11",
"wchat12",
"wchat13",
"wchat14",
"wchat15",
"wchat16",
"wchat17",
"wchat18",
"wchat19",
"wchat21",
"wchat22",
"wchat23",
"wchat24",
"wchat25",
"wchat26",
"wchat28",
"wchat29",
"wchat30",
"wchat31",
"wchat32",
"wchat33",
"wchat34",
"wchat35",
"wchat36",
"wchat37",
"wchat38",
"wchat39",
"wchat40",
"wchat41",
"wchat43",
"wchat44",
"wchat45",
"wchat46",
"wchat47",
"wchat48",
"wchat49",
"wchat50",
"wchat51",
"wchat52",
"wchat53",
"wchat54",
"wchat55",
"wchat56",
"wchat57",
"wchat58",
"wchat59",
"wchat60",
"wchat61",
"wchat62",
"wchat63",
"wchat64",
"wchat66",
"wchat67",
"wchat68",
"wchat69",
"wchat70",
"wchat71",
"wchat72",
"wchat73",
"wchat74",
]