import asyncio
import random
from argparse import Namespace

from cmd2 import CommandSet, categorize, with_argparser

from stardust.apps.manage_capture import start_capture
from stardust.apps.myfreecams.db_myfreemcams import DbMfc
from stardust.apps.myfreecams.handleurls import MfcNetActions
from stardust.apps.myfreecams.models_mfc import MFCModel, MfcSession
from stardust.config.arg_parser import get_parser
from stardust.utils.applogging import HelioLogger
from stardust.utils.general import chk_streamer_name
from stardust.utils.handle_m3u8 import HandleM3u8

log = HelioLogger()

db=DbMfc('myfreecams')
class MyFreeCams(CommandSet):

    def __init__(self):
        super().__init__()

    @with_argparser(get_parser())
    def do_get(self, streamer: Namespace):
        """Capture a streamer

        example:
        MFC--> get <streamer's_name>
        """

        name_ = str(streamer.streamer)

        if not chk_streamer_name(name_):
            return

        if db.query_pid(name_):
            log.warning(f"Already capturing {name_} [MFC]")
            return None

        json_ = asyncio.run(MfcNetActions().get_user_profile([name_]))
        url_ = parse_profile(json_[0])

        if not url_:
            return None

        if not db.write_seek((name_)):
            log.error(f"Failed to update {name_}")
            return

        new_m3u8 = HandleM3u8(url_).new_mfc_m3u8()

        db.write_url((url_,name_))

        streamer_data = (name_, "mfc", str(new_m3u8))

        if not start_capture([streamer_data]):
            log.error(f'Capture for {name_} failed')

    def do_stop(self, ns: Namespace):
        """Stop Streamer Capture

        example:
        MFC--> stop <streamer's_name>
        """
        pass

    def do_block(self, ns: Namespace):
        """Block streamer from long captures
        MFC--> get my_fav_girl
        """
        pass

    categorize((do_get, do_stop, do_block), "MyFreeCams Streamer")


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
