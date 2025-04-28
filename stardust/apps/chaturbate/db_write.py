from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
import sqlite3

from stardust.config.constants import FailVideoContext
from stardust.config.settings import get_db_setting
from stardust.utils.applogging import HelioLogger

log = HelioLogger()
DB = get_db_setting().CB_DB_FOLDER


@contextmanager
def connect_write():
    pragma_write = """
    PRAGMA journal_mode=MEMORY;
    PRAGMA temp_store = MEMORY;
    PRAGMA synchronous=OFF;
    PRAGMA locking_mode = exlusive;
    PRAGMA cache_size = 2000000;
    """
    with sqlite3.connect(DB) as conn:
        conn.executescript(pragma_write)
        yield conn


def write_db(sql: str, values):
    write = None
    try:
        with connect_write() as conn:
            write = conn.execute(sql, values)

        return bool(write)
    except sqlite3.Error as e:
        msg = f"{Path(__file__).parts[-1]} {write_db.__name__}() {e}"
        log.error(msg)


def write_cb_many(sql: str, values):
    remove_index = "DROP INDEX IF EXISTS idx_num;"
    add_index = (
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_streamer ON chaturbate (streamer_name);"
    )

    with connect_write() as conn:
        conn.execute(remove_index)
        try:
            conn.execute("BEGIN TRANSACTION")
            conn.executemany(sql, values)
            conn.execute("END TRANSACTION")
        except Exception as e:
            log.error(e)

        conn.execute(add_index)
        # 'PRAGMA synchronous = OFF'
        # display_pragma(conn)
        conn.executescript("ANALYZE; VACUUM;")


def write_db_streamers(value: list):
    sql = """
        INSERT INTO chaturbate (
        streamer_name, age, last_broadcast, followers, viewers, location_, country, is_new, tags,bio_chk_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (streamer_name)
        DO UPDATE SET 
        age=EXCLUDED.age,
        last_broadcast=EXCLUDED.last_broadcast,
        followers=EXCLUDED.followers,
        viewers=EXCLUDED.viewers,
        most_viewers=MAX(most_viewers, EXCLUDED.viewers),
        location_=EXCLUDED.location_,
        country=EXCLUDED.country,
        is_new=EXCLUDED.is_new,
        tags=EXCLUDED.tags,
        bio_chk_date=EXCLUDED.bio_chk_date
        """
    write_cb_many(sql, value)


def write_m3u8(value: list[tuple[str, str]]):
    sql = """
        UPDATE chaturbate
        SET url_= ?
        WHERE streamer_name = ?
    """
    status = write_cb_many(sql, value)
    return status


def write_api_data(value: list):
    sql = """
        INSERT INTO chaturbate (
        streamer_name, age, last_broadcast, viewers, tags)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (streamer_name)
        DO UPDATE SET
        age=EXCLUDED.age,
        last_broadcast=IFNULL(last_broadcast, EXCLUDED.last_broadcast),
        viewers=EXCLUDED.viewers,
        most_viewers=MAX(most_viewers, EXCLUDED.viewers),
        tags=EXCLUDED.tags,
        bio_chk_date=DATE('now', 'localtime')
    """

    write_cb_many(sql, value)


def write_pid(value: tuple[int, str]):
    pid, name_ = value
    today = datetime.now().replace(microsecond=0)
    # SET recorded=recorded+1,
    sql = "Update chaturbate SET pid=?, last_capture=?, last_broadcast=? WHERE streamer_name=?"
    args = (pid, today, today, name_)

    if not write_db(sql, args):
        log.error(f"Failed to update {name_}'s pid")


def write_remove_pid(value: int):
    sql = "UPDATE chaturbate SET pid=? WHERE pid=?"
    write_db(sql, (None, value))


def write_get_streamer(value: str):
    name_ = value
    today = datetime.now().replace(microsecond=0)
    sql = """
        INSERT INTO chaturbate (streamer_name, seek_capture) 
        VALUES (?, ?) 
        ON CONFLICT (streamer_name) 
        DO UPDATE SET 
        seek_capture=EXCLUDED.seek_capture
        WHERE seek_capture IS NULL
        """
    args = (
        name_,
        today,
    )
    write = write_db(sql, args)

    if not write:
        log.error(f"Failed to add: {name_}")


def write_remove_seek(name_):
    sql = "UPDATE chaturbate SET seek_capture=?, pid=? WHERE streamer_name=?"
    args = (None, None, name_)

    if not write_db(sql, args):
        log.error(f"Unable to stop capture for {name_} [CB]")


def write_block_info(data):
    name_, *reason = data
    reason = " ".join(reason)

    sql = """
        UPDATE chaturbate 
        SET block_date=?, seek_capture=?, notes=IFNULL(notes, '')||?
        WHERE streamer_name=?
        """
    arg = (date.today(), None, f"{reason}", name_)
    if not write_db(sql, arg):
        log.error(f"Block command failed for {name_} [CB]")


def write_videocontext_fail(values: list[FailVideoContext]):
    new_values = []
    for value in values:
        new_values.append((value.status, value.detail, value.code, value.name_))
    sql = """
        UPDATE chaturbate
        SET bio_chk_date=DATETIME('now', 'localtime'),
        bio_fail_date=DATETIME('now', 'localtime'),
        bio_fail_status=?,
        bio_fail_detail=?,
        bio_fail_code=?
        WHERE streamer_name=?
        """

    write_cb_many(sql, new_values)


def write_data_review(value: list[tuple[str, Path]]):
    sql = """
        INSERT INTO chaturbate (streamer_name, data_review) 
        VALUES (?, ?) 
        ON CONFLICT (streamer_name) 
        DO UPDATE SET 
        data_review=EXCLUDED.data_review
        """
    write_cb_many(sql, value)


def write_data_keep(value: list[tuple[str, Path]]):
    sql = """
        INSERT INTO chaturbate (streamer_name, data_keep) 
        VALUES (?, ?) 
        ON CONFLICT (streamer_name) 
        DO UPDATE SET 
        data_keep=EXCLUDED.data_keep
        """
    write_cb_many(sql, value)


def write_data_size(values):
    sql="""
        UPDATE chaturbate
        SET
        data_total=IFNULL(data_total ,0) + ?
        WHERE streamer_name = ?
        """

    write_db(sql, values)