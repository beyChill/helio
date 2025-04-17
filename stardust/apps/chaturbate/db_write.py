from datetime import datetime
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


def write_cb_url(value: list[tuple[str, str]]):
    sql = """
        UPDATE chaturbate
        SET url_= ?
        WHERE streamer_name = ?
    """
    status = write_cb_many(sql, value)
    return status


def write_cb_api_data(value: list):
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


def write_pid(arg: tuple[int, str]):
    pid, name_ = arg
    today = datetime.now().replace(microsecond=0)
    # SET recorded=recorded+1,
    sql = "Update chaturbate SET pid=?, last_capture=?, last_broadcast=? WHERE streamer_name=?"
    args = (pid, today, today, name_)

    if not write_db(sql, args):
        log.error(f"Failed to update {name_}'s pid")


def write_remove_pid(value: int):
    sql = "UPDATE chaturbate SET pid=? WHERE pid=?"
    write_db(sql, (None, value))
