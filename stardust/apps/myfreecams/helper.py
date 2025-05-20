import random
from pathlib import Path

import imagehash
from PIL import Image

from stardust.apps.myfreecams.json_models import Lookup, LookupSession
from stardust.config.settings import get_setting
from stardust.utils.applogging import HelioLogger, loglvl

log = HelioLogger()
REF_IMG_DIR = get_setting().DIR_HASH_REF


# Couldn't determine method to get average_hash
# from a list comprehension. Using __str__()
# otherwise it returns hash map. Issue absent
# a for loop
HASH_REFS = [
    (imagehash.average_hash(Image.open(path_)).__str__())
    for path_ in REF_IMG_DIR.glob("*.jpg")
]


def calc_img_hash(image: Path):
    hash = imagehash.average_hash(Image.open(image))
    return hash


def get_name_url(streamer: Lookup):
    name_ = streamer.method.split("/")[-1]
    session = streamer.result.user.sessions[-1]
    streamer_id = streamer.result.user.id
    playlist_url = make_playlist(session, streamer_id)
    return (playlist_url, name_)


def make_playlist(session: LookupSession, streamer_id: int):
    server = mfc_server_offset(session.vidserver_id)
    phase_fix = ""
    phase = session.phase

    if phase == "a":
        phase_fix = "a_"
    pid = str(session.platform_id)

    # 8 is mininum number of digits for a url's id
    id = str(streamer_id).zfill(8)

    session_name = "".join([phase_fix, pid, id])

    nc_value = random.random()

    url = f"https://edgevideo.myfreecams.com/llhls/NxServer/{server}/ngrp:mfc_{session_name}.f4v_cmaf/playlist.m3u8?nc={nc_value}&v=1.97.23"

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


MFC_VIDEO_STATUS = {
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
            log.app(loglvl.OFFLINE, f"{name_} [{slug}]")
            return None

        status = MFC_VIDEO_STATUS.get(
            streamer.result.user.sessions[-1].vstate, "unknown"
        )

        if status != "public":
            log.warning(f"{name_} {slug} is {status}")
            return None
        return streamer
    except Exception as e:
        log.error(e)
        return None
