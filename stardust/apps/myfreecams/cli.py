import asyncio
import os
import random
from argparse import Namespace
from signal import SIGTERM

from cmd2 import CommandSet, categorize, with_argparser

from stardust.apps.manage_capture import start_capture
from stardust.apps.myfreecams.db_myfreemcams import DbMfc
from stardust.apps.myfreecams.handleurls import MfcNetActions

# from stardust.apps.myfreecams.models_mfc import MFCModel, MfcSession
from stardust.apps.myfreecams.helper import parse_profile
from stardust.config.arg_parser import get_parser
from stardust.utils.applogging import HelioLogger
from stardust.utils.general import chk_streamer_name
from stardust.utils.handle_m3u8 import HandleM3u8

log = HelioLogger()

db = DbMfc("myfreecams")


class MyFreeCams(CommandSet):
    def __init__(self):
        self.slug = "MFC"
        super().__init__()

    @with_argparser(get_parser())
    def do_get(self, streamer: Namespace):
        """Initiate capture for a streamer

        example:
        MFC--> get <streamer's_name>
        """

        name_ = str(streamer.streamer)

        if not chk_streamer_name(name_):
            return

        if db.query_pid(name_):
            log.warning(f"Already capturing {name_} [{self.slug}]")
            return None

        json_ = asyncio.run(MfcNetActions().get_user_profile([name_]))
        url_ = parse_profile(json_[0])

        if not url_:
            return None

        if not db.write_seek((name_)):
            log.error(f"Failed to update {name_}")
            return
        
        if isinstance(url_,tuple):
            return
        
        new_m3u8 = HandleM3u8(url_).new_mfc_m3u8()

        db.write_url((new_m3u8, name_))

        streamer_data = (name_, self.slug.lower(), str(new_m3u8))

        if not start_capture([streamer_data]):
            log.error(f"Capture for {name_} failed")

    @with_argparser(get_parser())
    def do_stop(self, streamer: Namespace) -> None:
        """Terminate a single capture session

        example:
        MFC--> stop <streamer's_name>
        """
        name_ = str(streamer.streamer)
        if not chk_streamer_name(name_):
            return None

        if pid := db.query_pid(name_):
            try:
                os.kill(pid, SIGTERM)
                db.write_stop_seek(name_)
                log.warning(f"Manual stop for {name_} [{self.slug}]")
                return None
            except OSError as e:
                msg = f"{e} for {name_}"
                log.error(msg)

        if not pid:
            log.info(f"Stopping seek for {name_} [{self.slug}]")

    def do_block(self, ns: Namespace):
        """Block streamer from long captures
        MFC--> get my_fav_girl
        """
        pass

    categorize((do_get, do_stop, do_block), "MyFreeCams Streamer")
