import asyncio
from argparse import Namespace

from cmd2 import (
    CommandSet,
    categorize,
    with_argparser,
)

import stardust.utils.heliologger as log
from stardust.apps.arg_parser import (
    block_reason,
    cap_status,
    get_streamer,
    long_inactive,
    stop_streamer,
)
from stardust.apps.chaturbate.handleurls import iNetCb
from stardust.apps.manage_app_db import HelioDB
from stardust.apps.manage_capture import start_capture
from stardust.apps.shared_cmds import cmd_cap, cmd_long, cmd_off, cmd_stop_process_id
from stardust.utils.general import chk_streamer_name
from stardust.utils.handle_m3u8 import HandleM3u8

"""
It appears single argparse, nargs=1, creates a list.
select first in list for arg.name inputs ie. [0]
"""


class Chaturbate(CommandSet):
    """Interact with Chaturbate streamers"""

    def __init__(self):
        self.slug = "CB"
        self.db = HelioDB()
        super().__init__()

    @with_argparser(get_streamer())
    def do_get(self, arg: Namespace):
        """
        example:
        CB--> get <streamer's_name>
        """
        name_ = str(arg.name)

        if not chk_streamer_name(name_):
            log.error("Use lower case letters, digits, or _ in the name")
            return None

        if self.db.query_process_id(name_, self.slug):
            log.warning(f"Already capturing {name_} [{self.slug}]")
            return None

        self.db.write_seek_capture(name_, self.slug)

        json_ = asyncio.run(iNetCb().get_ajax_url([name_]))

        if not (url_ := json_[-1]["url"]):
            log.warning(f"{name_} is {json_[-1]['room_status']}")
            return None

        if (new_m3u8 := asyncio.run(HandleM3u8(url_).cb_m3u8())) is None:
            log.error(f"Problem with the m3u8 for {name_} {self.slug}")
            return

        self.db.write_capture_url((new_m3u8))

        best_uri, *_ = new_m3u8

        streamer_data = (name_, self.slug.lower(), best_uri)

        if not start_capture(streamer_data):
            log.error(f"Capture for {name_} failed")

    @with_argparser(stop_streamer())
    def do_stop(self, arg: Namespace) -> None:
        """
        example:
        CB--> stop <streamer's_name>
        """
        name_ = str(arg.name)

        if not chk_streamer_name(name_):
            print("oops")
            return None

        cmd_stop_process_id(name_, self.slug)

    @with_argparser(block_reason())
    def do_block(self, arg: Namespace) -> None:
        name_ = str(arg.name)
        if not chk_streamer_name(name_):
            return None

        reason = "".join(arg.reason)

        self.db.write_block_reason((name_, self.slug, reason))

    @with_argparser(long_inactive())
    def do_long(self, num: Namespace):
        cmd_long(num)

    def _query_streamer_pid(self, name_):
        data = self.db.query_process_id(name_, self.slug)

        if data:
            log.error(f"Already capturing {name_} [{self.slug}]")
            return None

        return data

    categorize((do_get, do_stop, do_block), "Chaturbate Streamer")
    categorize((do_long), "Site Streamer Status")
