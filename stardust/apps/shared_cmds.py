import os
from signal import SIGTERM

from tabulate import tabulate

from stardust.apps.manage_app_db import HelioDB
from stardust.utils.applogging import HelioLogger, loglvl

log = HelioLogger()
db = HelioDB()


def cmd_stop_process_id(name_: str, slug: str):
    if pid := db.query_process_id(name_, slug):
        try:
            os.kill(pid, SIGTERM)
            log.warning(f"Manually stopping {name_} [{slug}]")
            db.write_rm_seek_capture(name_, slug)
            return None
        except OSError as e:
            db.write_rm_seek_capture(name_, slug)
            if e.errno == 3:
                log.error(f"No such process id for {name_} [{slug}]")
                return None

            msg = f"A problem occurred while stopping {name_} [{slug}]"
            log.error(msg)


def cmd_stop_all_captures():
    if not (results := db.query_all_db_process_id()):
        return None

    try:
        {remove_pids(result) for result in results}
    except Exception as e:
        log.error(e)


def remove_pids(results: map):

    name_, slug, process_id = results
    try:
        os.kill(process_id, SIGTERM)
        log.warning(f"Manually stopping {name_} [{slug}]")
        db.write_rm_seek_capture(name_, slug)
        return None
    except OSError as e:
        db.write_rm_seek_capture(name_, slug)
        if e.errno == 3:
            log.warning(f"Invalid process ID for {name_} [{slug}]. Removed ID")
            return None
        log.error(f"Unknown error while removing process id for {name_} [{slug}]")


def cmd_cap(sort_opt):
    sort = sort_options(sort_opt)
    if not (query := db.query_active_capture(sort)):
        log.warning("Presently capturing zero streamers")
        return None

    head = ["Streamers", "Site", "Capturing", "Data (GB)"]
    print_table(query, head)


def cmd_off(sort_opt) -> None:
    sort = sort_options(sort_opt)
    if not (query := db.query_seek_offline(sort)):
        log.warning("Zero streams have capture status")
        return None
    head = ["Streamers", "Site", "Recent Stream", "Data (GB)"]
    print_table(query, head)


def cmd_long(num):
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
        "site": "slug",
    }
    sort = SORT_OPTIONS.get(option, "name")

    return sort


def print_table(query: list | set, head: list):
    print(
        tabulate(
            query,
            headers=head,
            tablefmt="pretty",
            colalign=("left", "left", "center", "center"),
        )
    )
