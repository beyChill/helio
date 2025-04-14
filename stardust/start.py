
import sys
from threading import Thread
from stardust.apps.chaturbate.api_streamer_online import run_cb_streamers
from stardust.apps.chaturbate.api_get_jsons import loop_cb_room_list

from stardust.cli.commandline import CLI
from stardust.database.db_base import db_init

threads = [
    Thread(target=run_cb_streamers, daemon=True),
    Thread(target=loop_cb_room_list, daemon=True),
]


if __name__=="__main__":
    db_init()
    for thread in threads:
        thread.start()

    cli = CLI()
    sys.exit(cli.cmdloop())