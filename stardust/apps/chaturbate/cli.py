from argparse import Namespace
import asyncio
from cmd2 import Cmd2ArgumentParser, CommandSet, with_argparser

from stardust.apps.chaturbate.validations import check_streamer_name
from stardust.apps.chaturbate.db_query import query_pid
from stardust.apps.chaturbate.db_write import write_get_streamer
from stardust.apps.chaturbate.handleurls import NetActions
from stardust.apps.chaturbate.manage_capture import start_capture
from stardust.utils.applogging import HelioLogger
from stardust.utils.general import process_hls


log = HelioLogger()


class Chaturbate(CommandSet):
    """Interact with Chaturbate streamers"""

    intro = log.info("Type help or ? for command infomation.\n")

    def __init__(self):
        super().__init__()

    get_parser = Cmd2ArgumentParser()
    get_parser.add_argument("name", nargs="?", help="Streamer name")

    @with_argparser(get_parser)
    def do_get(self, streamer: Namespace):
        name_ = streamer.name
        if not check_streamer_name(name_):
            return None

        (pid,) = query_pid(name_)
        if isinstance(pid, int):
            log.warning(f"Already capturing {name_} [CB]")
            return None

        write_get_streamer(name_)
        data = asyncio.run(NetActions().get_ajax_url([name_]))
        url_ = ""
        for d in data:
            url_ = d["url"]

        if not url_:
            return None
        new_url = asyncio.run(NetActions().get_m3u8(url_))

        streamer_data = process_hls([new_url])

        start_capture(streamer_data)
