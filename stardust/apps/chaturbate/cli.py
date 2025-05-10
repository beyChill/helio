import asyncio
from argparse import Namespace

from cmd2 import (
    CommandSet,
    categorize,
    with_argparser,
)

from stardust.apps.chaturbate.db_chaturbate import DbCb

from stardust.apps.chaturbate.handleurls import NetActions
from stardust.apps.manage_capture import start_capture
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

"""
It appears single argparse, nargs=1, creates a list.
select first in list for arg.name inputs ie. [0]
"""

log = HelioLogger()


class Chaturbate(CommandSet):
    """Interact with Chaturbate streamers"""

    def __init__(self):
        self.slug = "CB"
        self.db = DbCb("chaturbate")
        super().__init__()

    @with_argparser(get_streamer())
    def do_get(self, arg: Namespace):
        """
        example:
        CB--> get <streamer's_name>
        """
        name_ = str(arg.name)

        if not chk_streamer_name(name_, self.slug):
            log.error("Use letters, digits, or _ in the name")
            return None

        if self.db.query_pid(name_):
            log.warning(f"Already capturing {name_} [{self.slug}]")
            return None

        self.db.write_seek_capture(name_)

        json_ = asyncio.run(NetActions().get_ajax_url([name_]))

        if not (url_ := json_[-1]["url"]):
            return None

        new_url = asyncio.run(NetActions().get_m3u8(url_))

        new_m3u8 = HandleM3u8(new_url).new_cb_m3u8()

        self.db.write_url((new_m3u8, name_))

        streamer_data = (name_, self.slug.lower(), str(new_m3u8))

        if not start_capture([streamer_data]):
            log.error(f"Capture for {name_} failed")

    @with_argparser(get_streamer)
    def do_stop(self, arg: Namespace) -> None:
        """
        example:
        CB--> stop <streamer's_name>
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

    def _query_streamer_pid(self, name_):
        data = self.db.query_pid(name_)

        if data is not None:
            log.error(f"Already capturing {name_} [CB]")
            return None

        return data

    categorize((do_get, do_stop, do_block), "Chaturbate Streamer")
    categorize((do_cap, do_long, do_off), "Site Streamer Status")
