import random
from stardust.apps.myfreecams.models_mfc import MFCModel, MfcSession
from stardust.utils.applogging import HelioLogger

log=HelioLogger()

def parse_profile(json_: MFCModel):
    name_ = json_.method.split("/")[-1]

    if json_.result.message != "user found":
        log.warning(
            f"{name_} is not a MFC model. Perhaps check spelling or capitalizaton"
        )
        return

    if not json_.result.user:
        return

    user_id = json_.result.user.id

    if not json_.result.user.sessions:
        log.warning(f"{name_} user is offline")
        return

    online_data = json_.result.user.sessions
    url = make_mfc_playlist(online_data[-1], user_id)
    return url


def make_mfc_playlist(data: MfcSession, user_id: int):
    offset = 0
    id = user_id
    if data.vidserver_id == 0:
        log.warning("Streamer is possibly offline")
        return None

    if 845 <= data.vidserver_id <= 1399:
        offset = 500

    if 1545 <= data.vidserver_id <= 1559:
        offset = 1000

    if 1600 <= data.vidserver_id <= 1944:
        offset = 700

    if 3000 <= data.vidserver_id <= 3040:
        offset = 1000

    server = data.vidserver_id - offset
    phase = data.phase

    # 8 in mininum number of digits for url's id
    if len(str(user_id)) < 8:
        id = f"0{user_id}"

    nc_value = random.random()

    url = f"https://edgevideo.myfreecams.com/llhls/NxServer/{server}/ngrp:mfc_{phase}1{id}.f4v_cmaf/playlist.m3u8?nc={nc_value}&v=1.97.23"

    return url