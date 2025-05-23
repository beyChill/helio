import asyncio
from argparse import Namespace

from cmd2 import CommandSet, categorize, with_argparser

from stardust.apps.manage_app_db import HelioDB
from stardust.apps.manage_capture import start_capture
from stardust.apps.myfreecams.handleurls import iNetMfc

from stardust.apps.myfreecams.helper import chk_online_status, make_playlist
from stardust.apps.shared_cmds import cmd_cap, cmd_long, cmd_off, cmd_stop_process_id
from stardust.apps.arg_parser import (
    block_reason,
    cap_status,
    get_streamer,
    long_inactive,
    stop_streamer,
)
from stardust.utils.applogging import HelioLogger
from stardust.utils.general import chk_streamer_name
from stardust.utils.handle_m3u8 import HandleM3u8

log = HelioLogger()


class MyFreeCams(CommandSet):
    def __init__(self):
        self.slug = "MFC"
        self.db = HelioDB()
        self.iNet = iNetMfc()
        super().__init__()

    @with_argparser(get_streamer())
    def do_get(self, arg: Namespace):
        """
        example:
        MFC--> get <streamer's_name>
        """

        name_ = str(arg.name).lower()

        if not chk_streamer_name(name_, self.slug):
            log.error("Use lower case, digits, and _")
            return

        if self.db.query_process_id(name_, self.slug):
            log.warning(f"Already capturing {name_} [{self.slug}]")
            return None

        if (data := asyncio.run(self.iNet.get_all_status([name_]))) is None:
            log.warning(f"The query for {name_} {self.slug} failed")
            return None

        if data[0].result.message == "user not found":
            log.warning(f"{name_} not a {self.slug} streamer")
            return

        self.db.write_seek_capture(name_, self.slug)

        if (streamer := chk_online_status(data[0], name_, self.slug)) is None:
            return None

        session = streamer.result.user.sessions[-1]
        streamer_id = streamer.result.user.id

        playlist_url = make_playlist(session, streamer_id)

        if (m3u8 := asyncio.run(HandleM3u8(playlist_url).mfc_m3u8())) is None:
            return None

        self.db.write_capture_url((m3u8, name_, self.slug))

        streamer_data = (name_, self.slug.lower(), str(m3u8))

        if not start_capture([streamer_data]):
            log.error(f"Capture for {name_} failed")

    @with_argparser(stop_streamer())
    def do_stop(self, arg: Namespace) -> None:
        """
        example:
        MFC--> stop <streamer's_name>
        """
        name_ = str(arg.name).lower()
        if not chk_streamer_name(name_, self.slug):
            return None

        cmd_stop_process_id(name_, self.slug)

    @with_argparser(block_reason())
    def do_block(self, arg: Namespace) -> None:
        name_ = str(arg.name).lower()
        if not chk_streamer_name(name_, self.slug):
            return None

        reason = "".join(arg.reason)

        self.db.write_block_reason((name_, reason))

    @with_argparser(cap_status())
    def do_cap(self, arg: Namespace) -> None:
        cmd_cap(arg.sort)

    @with_argparser(cap_status())
    def do_off(self, arg: Namespace) -> None:
        cmd_off(arg.sort)

    @with_argparser(long_inactive())
    def do_long(self, num: Namespace):
        cmd_long(num)

    categorize((do_get, do_stop, do_block), "MyFreeCams Streamer")
    categorize((do_cap, do_long, do_off), "Streamer Status")
