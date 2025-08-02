import sys
from threading import Thread

from stardust.apps.chaturbate.api_get_jsons import loop_cb_all_online
from stardust.apps.chaturbate.api_streamer_online import loop_cb_seek_capture
from stardust.apps.myfreecams.api_streamer_online import loop_mfc_seek_capture
from stardust.apps.myfreecams.api_ws_json import loop_mfc_online_streamers
from stardust.apps.shared_cmds import is_process_active
from stardust.cli.commandline import HelioCli
from stardust.database.db_base import db_init

__all__ = ["main"]

threads = {
    Thread(target=loop_cb_all_online, daemon=True),
    Thread(target=loop_cb_seek_capture, daemon=True),
    Thread(target=loop_mfc_seek_capture, daemon=True),
    Thread(target=loop_mfc_online_streamers, daemon=True),
}


def run_threads():
    _ = {thread.start() for thread in threads}


def main():
    db_init()
    is_process_active()
    # run_threads()
    cli = HelioCli()
    sys.exit(cli.cmdloop())


if __name__ == "__main__":
    main()
