import os
from signal import SIGTERM

from tabulate import tabulate

import stardust.utils.heliologger as log
from stardust.apps.manage_app_db import HelioDB

db = HelioDB()


def cmd_stop_process_id(name_: str, slug: str):
    db.write_rm_seek_capture(name_, slug)
    if pid := db.query_process_id(name_, slug):
        try:
            os.kill(pid, SIGTERM)
            log.stopped(name_, f"[{slug}]")
            
        except OSError as e:
            if e.errno == 3:
                log.error(f"Invalid process id for {name_} [{slug}]")
                return None

            msg = f"A problem occurred while stopping {name_} [{slug}]"
            log.error(msg)
            
    return None


def cmd_stop_all_captures():
    if not (results := db.query_all_db_process_id()):
        return None

    try:
        {remove_pids(result) for result in results}
    except Exception as e:
        log.error(e)


def is_process_active():
    """
    Function will not remove an active capture.
        There, at capture's end the streamer will
        require a manual restart (get cmd) or wait
        for timed site query for streamer status.
    """
    if not (results := db.query_all_db_process_id()):
        return None
    {check_process_ids(result) for result in results}


def check_process_ids(results: tuple):
    name_, slug, process_id = results
    try:
        os.kill(process_id, 0)
    except OSError as e:
        handle_process_id_error(name_, slug,process_id, e)

def remove_pids(results: tuple):
    name_, slug, process_id = results
    try:
        os.kill(process_id, SIGTERM)
        log.stopped(f"{name_} [{slug}]")
        db.write_rm_process_id(process_id)
        return None
    except OSError as e:
        handle_process_id_error(name_, slug,process_id, e)

def handle_process_id_error(name_, slug,process_id, e:OSError):
        db.write_rm_process_id(process_id)
        if e.errno == 3:
            log.stopped(f"Invalid capture for {name_} [{slug}]. Removed ID")
            return None
        log.error(f"Unknown error with process id for {name_} [{slug}]")

def cmd_cap(sort_opt):
    sort = sort_options(sort_opt)
    if not (query := db.query_active_capture(sort)):
        log.info("Presently capturing zero streamers")
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

    log.success(f"Checked inactivity for {len(streamers)} streamers")
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
