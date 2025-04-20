from datetime import date, datetime
from pathlib import Path

from stardust.config.constants import FailVideoContext
from stardust.database.db_base import write_cb_many, write_db
from stardust.utils.applogging import HelioLogger

log = HelioLogger()


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

def write_videocontext_fail(values:list[FailVideoContext]):
    new_values=[]
    for value in values:
        new_values.append((value.status,value.detail,value.code,value.name_))
    sql="""
        UPDATE chaturbate
        SET bio_chk_date=DATETIME('now', 'localtime'),
        bio_fail_date=DATETIME('now', 'localtime'),
        bio_fail_status=?,
        bio_fail_detail=?,
        bio_fail_code=?
        WHERE streamer_name=?
        """
    
    write_cb_many(sql, new_values)

def write_data_review(value: list[tuple[str,Path]]):
    sql = """
        INSERT INTO chaturbate (streamer_name, data_review) 
        VALUES (?, ?) 
        ON CONFLICT (streamer_name) 
        DO UPDATE SET 
        data_review=EXCLUDED.data_review
        """
    write_cb_many(sql, value)

def write_data_keep(value: list[tuple[str,Path]]):
    sql = """
        INSERT INTO chaturbate (streamer_name, data_keep) 
        VALUES (?, ?) 
        ON CONFLICT (streamer_name) 
        DO UPDATE SET 
        data_keep=EXCLUDED.data_keep
        """
    write_cb_many(sql, value)
