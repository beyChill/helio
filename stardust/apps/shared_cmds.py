import os
from signal import SIGTERM

from tabulate import tabulate
from stardust.apps.chaturbate.db_chaturbate import DbCb
from stardust.apps.myfreecams.db_myfreemcams import DbMfc
from stardust.utils.applogging import HelioLogger, loglvl

log = HelioLogger()


def cmd_stop_process_id(name_: str, slug: str, db: DbCb | DbMfc):
    if pid := db.query_process_id(name_):
        try:
            os.kill(pid, SIGTERM)
            log.warning(f"Manually stopping {name_} [{slug.upper()}]")
            db.write_rm_seek_capture(name_)
            return None
        except OSError as e:
            db.write_rm_seek_capture(name_)
            if e.errno == 3:
                log.error(f"No such process id for {name_} [{slug.upper()}]")
                return None

            msg = f"A problem occurred while stopping {name_} [{slug.upper()}]"
            log.error(msg)


def cmd_cap(sort_opt, db: DbCb | DbMfc):
    print(type(db))
    sort = sort_options(sort_opt)
    if not (query := db.query_active_capture(sort)):
        log.warning("Presently capturing zero chaturbate streamers")
        return None

    head = ["Streamers", "Capturing", "Data (GB)"]
    print_table(query, head)


def cmd_off(sort_opt, db: DbCb | DbMfc) -> None:
    sort = sort_options(sort_opt)
    if not (query := db.query_seek_offline(sort)):
        log.warning("Following zero streamers")
        return None
    head = ["Streamers", "Recent Stream", "Data (GB)"]
    print_table(query, head)


def cmd_long(num, db: DbCb | DbMfc):
    streamers = db.query_long_offline(num.days)

    if len(streamers) == 0:
        log.warning("Zero streamers for inactive check")
        return

    log.app(loglvl.SUCCESS, f"Checked inactivity for {len(streamers)} streamers")
    db.write_last_broadcast(streamers)


def sort_options(option):
    SORT_OPTIONS: dict[str, str] = {
        "name": "streamer_name",
        "size": "data_total",
        "date": "seek_capture",
    }
    sort = SORT_OPTIONS.get(option)

    return sort


def print_table(query: list, head: list):
    print(
        tabulate(
            query,
            headers=head,
            tablefmt="pretty",
            colalign=("left", "center", "center"),
        )
    )
