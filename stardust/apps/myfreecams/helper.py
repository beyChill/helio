import random
from pathlib import Path

import imagehash
from PIL import Image

from stardust.apps.myfreecams.models_mfc import MfcLookup, MfcSession
from stardust.config.settings import get_setting
from stardust.utils.applogging import HelioLogger

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


def parse_profile(json_: MfcLookup, fetch: str = "one"):
    name_ = json_.method.split("/")[-1]

    if json_.result.message != "user found":
        log.warning(
            f"{name_} is not a MFC model. Perhaps check spelling or capitalizaton"
        )
        return (None, name_)

    user_id = json_.result.user.id

    if not json_.result.user.sessions:
        log.warning(f"{name_} is offline")
        return (None, name_)


    if json_.result.user.sessions[0].vstate != 0:
        print(json_.result.user.sessions[-1].vstate)
        status =mfc_video_status.get(json_.result.user.sessions[-1].vstate,'unknown')

        if status==2 and json_.result.user.sessions[0].phase=='':
            status='offline'

        log.warning(f"{name_} is {status}")
        return (None, name_)

    online_data = json_.result.user.sessions
    url = make_mfc_playlist(online_data[-1], user_id)

    if fetch == "all":
        return (url, name_)

    return url


def make_mfc_playlist(data: MfcSession, user_id: int):
    server = mfc_server_offset(data.vidserver_id)

    # 8 is mininum number of digits for a url's id
    id = str(user_id).zfill(8)

    nc_value = random.random()

    url = f"https://edgevideo.myfreecams.com/llhls/NxServer/{server}/ngrp:mfc_{data.phase}1{id}.f4v_cmaf/playlist.m3u8?nc={nc_value}&v=1.97.23"

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

mfc_video_status={
    0:'public',
    2:'away',
    12:'private',
    13:'group show',
    14:'club',
    90:'hidden',
    127:'offline',
    None:'offline'
}