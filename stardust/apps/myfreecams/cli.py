import asyncio
from argparse import Namespace

from cmd2 import CommandSet, categorize, with_argparser

from stardust.apps.manage_capture import start_capture
from stardust.apps.myfreecams.db_myfreemcams import DbMfc
from stardust.apps.myfreecams.handleurls import MfcNetActions

from stardust.apps.myfreecams.helper import parse_profile
from stardust.apps.shared_cmds import cmd_cap, cmd_long, cmd_off, cmd_stop_process_id
from stardust.apps.arg_parser import (
    block_reason,
    cap_status,
    get_streamer,
    long_inactive,
)
from stardust.utils.applogging import HelioLogger
from stardust.utils.general import chk_streamer_name
from stardust.utils.handle_m3u8 import HandleM3u8

log = HelioLogger()


class MyFreeCams(CommandSet):
    def __init__(self):
        self.slug = "MFC"
        self.db = DbMfc("myfreecams")
        self.iNet = MfcNetActions()
        super().__init__()

    @with_argparser(get_streamer())
    def do_get(self, arg: Namespace):
        """
        example:
        MFC--> get <streamer's_name>
        """

        name_ = str(arg.name)

        if not chk_streamer_name(name_, self.slug):
            log.error("Use lower case, digits, and _")
            return

        if self.db.query_pid(name_):
            log.warning(f"Already capturing {name_} [{self.slug}]")
            return None

        self.db.write_seek_capture(name_)

        json_ = asyncio.run(self.iNet.get_user_profile([name_]))

        if not (url_ := parse_profile(json_[0])):
            return None

        if isinstance(url_, tuple):
            return

        m3u8_text = asyncio.run(self.iNet.get_m3u8(url_))

        new_m3u8 = HandleM3u8(m3u8_text).mfc_m3u8()

        self.db.write_url((new_m3u8, name_))

        streamer_data = (name_, self.slug.lower(), str(new_m3u8))

        if not start_capture([streamer_data]):
            log.error(f"Capture for {name_} failed")

    @with_argparser(get_streamer())
    def do_stop(self, arg: Namespace) -> None:
        """
        example:
        MFC--> stop <streamer's_name>
        """
        name_ = str(arg.name)
        if not chk_streamer_name(name_, self.slug):
            return None

        cmd_stop_process_id(name_, self.slug, self.db)

    @with_argparser(block_reason())
    def do_block(self, arg: Namespace) -> None:
        name_ = str(arg.name)
        if not chk_streamer_name(name_, self.slug):
            return None

        reason = "".join(arg.reason)

        self.db.write_block_reason((name_, reason))

    @with_argparser(cap_status())
    def do_cap(self, arg: Namespace) -> None:
        cmd_cap(arg.sort, self.db)

    @with_argparser(cap_status())
    def do_off(self, arg: Namespace) -> None:
        cmd_off(arg.sort, self.db)

    @with_argparser(long_inactive())
    def do_long(self, num: Namespace):
        cmd_long(num, self.db)

    categorize((do_get, do_stop, do_block), "MyFreeCams Streamer")
