from argparse import Namespace
import asyncio
import os
from signal import SIGTERM
from cmd2 import Cmd, Cmd2ArgumentParser, CommandSet, with_argparser
from tabulate import tabulate
from stardust.apps.chaturbate.api_videocontext import handle_response
from stardust.apps.chaturbate.validations import check_streamer_name
from stardust.apps.chaturbate.db_query import (
    query_capture,
    query_long_offline,
    query_offline,
    query_pid,
)
from stardust.apps.chaturbate.db_write import (
    write_block_info,
    write_get_streamer,
    write_remove_seek,
)
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
        del Cmd.do_macro
        del Cmd.do_run_pyscript
        del Cmd.do_shortcuts
        del Cmd.do_shell
        del Cmd.do_alias
        del Cmd.do_edit
        del Cmd.do_set
        del Cmd.do_quit
        del Cmd.do_run_script

    get_parser = Cmd2ArgumentParser()
    get_parser.add_argument("name", nargs=1, help="Streamer name")

    @with_argparser(get_parser)
    def do_get(self, streamer: Namespace):
        name_ = streamer.name
        if not check_streamer_name(name_):
            return None

        if self._query_streamer_pid(name_):
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

    @with_argparser(get_parser)
    def do_stop(self, streamer: Namespace) -> None:
        name_ = streamer.name
        if not check_streamer_name(name_):
            return None

        if not (pid := self._query_streamer_pid(name_)):
            return None

        try:
            os.kill(pid, SIGTERM)
        except OSError as e:
            msg = f"{e} for {name_}"
            log.error(msg)
        write_remove_seek(name_)

    block_parser = Cmd2ArgumentParser()
    block_parser.add_argument("name", nargs=1, help="Streamer name")
    block_parser.add_argument("reason", nargs="+", help="Reason for block")

    @with_argparser(block_parser)
    def do_block(self, streamer: Namespace) -> None:
        name_ = streamer.name[0]
        if not check_streamer_name(name_):
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
            print("Following zero streamers")
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
        print(len(streamers))
        if len(streamers) == 0:
            log.warning("Query return zero streamers")
            return

        self.update_last_broadcast(streamers)

    def update_last_broadcast(self, streamers: list):
        iNet = NetActions()
        results = asyncio.run(iNet.get_all_bio(streamers))
        print(results)
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
        data = query_pid(name_)

        if data is None:
            log.error(
                f"Problem with query for {name_} [CB]\n\t Check spelling or streamer capture status"
            )
            return None

        (pid,) = data

        if not isinstance(pid, int):
            log.warning(f"{name_} [CB] is not in capture status")
            return None

        return pid
