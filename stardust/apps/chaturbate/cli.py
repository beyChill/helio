import asyncio
import os
from argparse import Namespace
from signal import SIGTERM

from cmd2 import (
    Cmd,
    Cmd2ArgumentParser,
    CommandSet,
    categorize,
    with_argparser,
)
from tabulate import tabulate

from stardust.apps.chaturbate.api_streamer_bio import handle_response
from stardust.apps.chaturbate.db_chaturbate import DbCb
from stardust.apps.chaturbate.db_query import (
    query_capture,
    query_long_offline,
    query_offline,
)
from stardust.apps.chaturbate.db_write import (
    write_block_info,
)
from stardust.apps.chaturbate.handleurls import NetActions
from stardust.apps.manage_capture import start_capture
from stardust.config.arg_parser import get_parser
from stardust.utils.applogging import HelioLogger
from stardust.utils.general import chk_streamer_name
from stardust.utils.handle_m3u8 import HandleM3u8

"""
It appears single argparse, nargs=1, creates a list.
select first in list for streamer.name inputs ie. [0]
"""

log = HelioLogger()
db = DbCb("chaturbate")


class Chaturbate(CommandSet):
    """Interact with Chaturbate streamers"""

    def __init__(self):
        self.slug = "CB"
        super().__init__()

    @with_argparser(get_parser())
    def do_get(self, streamer: Namespace):
        """
        example:
        CB--> get <streamer's_name>
        """
        name_ = str(streamer.streamer)

        if not chk_streamer_name(name_, self.slug):
            log.error("Use letters, digits, or _ in the name")
            return None

        if db.query_pid(name_):
            log.warning(f"Already capturing {name_} [{self.slug}]")
            return None

        if not db.write_seek((name_)):
            return

        json_ = asyncio.run(NetActions().get_ajax_url([name_]))
        
        if not (url_:=json_[-1]['url']):
            return None

        new_url = asyncio.run(NetActions().get_m3u8(url_))
        url, url_as_text = new_url

        new_m3u8 = HandleM3u8(url).new_cb_m3u8()

        db.write_url((new_m3u8, name_))
        
        streamer_data = (name_, self.slug.lower(), str(new_m3u8))

        if not start_capture([streamer_data]):
            log.error(f"Capture for {name_} failed")

    @with_argparser(get_parser)
    def do_stop(self, streamer: Namespace) -> None:
        """Terminate a single capture session

        example:
        CB--> stop <streamer's_name>
        """
        name_ = str(streamer.streamer)
        if not chk_streamer_name(name_,self.slug):
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

    block_parser = Cmd2ArgumentParser()
    block_parser.add_argument("name", nargs=1, help="Streamer name")
    block_parser.add_argument("reason", nargs="+", help="Reason for block")

    @with_argparser(block_parser)
    def do_block(self, streamer: Namespace) -> None:
        name_ = streamer.name[0]
        if not chk_streamer_name(name_,self.slug):
            return None

        reason = "".join(streamer.reason)

        write_block_info((name_, reason))

    def my_choices_provider(self):
        sort = ["name", "number", "size"]
        return sort

    capture_parser = Cmd2ArgumentParser()
    capture_parser.add_argument(
        "sort", choices=["date", "name", "size"], help="Use one option"
    )

    @with_argparser(capture_parser)
    def do_cap(self, streamer: Namespace) -> None:
        sort = self._sort_options(streamer.sort)

        if not (query := query_capture(sort)):
            log.warning("Presently capturing zero chaturbate streamers")
            return None

        head = ["Streamers", "Capturing", "Data"]
        self._print_table(query, head)

    @with_argparser(capture_parser)
    def do_off(self, streamer: Namespace) -> None:
        sort = self._sort_options(streamer.sort)

        if not (query := query_offline(sort)):
            log.warning("Following zero streamers")
            return None

        head = ["Streamers", "Recent Stream", "Data"]
        self._print_table(query, head)

    long_parser = Cmd2ArgumentParser()
    long_parser.add_argument(
        "days",
        type=int,
        choices=[0, 7, 14, 31, 60, 90, 120, 180, 365, 730],
        help="Use one option",
    )

    @with_argparser(long_parser)
    def do_long(self, num: Namespace):
        streamers = query_long_offline(num.days)

        if len(streamers) == 0:
            log.warning("Query return zero streamers")
            return

        self.update_last_broadcast(streamers)

    def update_last_broadcast(self, streamers: list):
        iNet = NetActions()
        results = asyncio.run(iNet.get_all_bio(streamers))

        handle_response(results)

    def _print_table(self, query: list, head: list):
        print(
            tabulate(
                query,
                headers=head,
                tablefmt="pretty",
                colalign=("left", "center", "center"),
            )
        )

    def _sort_options(self, option):
        SORT_OPTIONS: dict[str, str] = {
            "name": "streamer_name",
            "size": "data_total",
            "date": "seek_capture",
        }
        sort = SORT_OPTIONS.get(option)

        return sort

    def _query_streamer_pid(self, name_):
        data = db.query_pid(name_)

        if data is not None:
            log.error(f"Already capturing {name_} [CB]")
            return None

        return data

    categorize((do_get, do_stop, do_block), "Chaturbate Streamer")
    categorize((do_cap, do_long, do_off), "Site Streamer Status")
