from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path
import sqlite3
from typing import Any

from stardust.config.settings import get_db_setting
from stardust.utils.applogging import HelioLogger

log = HelioLogger()
DB = get_db_setting().CB_DB_FOLDER


@contextmanager
def connect_query():
    pragma_query = """
        PRAGMA temp_store = MEMORY;
        PRAGMA synchronous=OFF;
        PRAGMA locking_mode = exlusive;
        """
    with sqlite3.connect(DB) as conn:
        conn.executescript(pragma_query)
        yield conn


def query_db(sql: str | tuple, action: str = "one"):
    data = []
    try:
        with connect_query() as conn:
            cursor = conn.cursor()

            try:
                if isinstance(sql, tuple):
                    sql_query, args = sql
                    cursor.execute(sql_query, args)

                if not isinstance(sql, tuple):
                    cursor.execute(sql)

            except Exception as e:
                log.error(f"{sql}")
                log.error(e)

            if action == "one":
                data: Any = cursor.fetchone()[0]

            if action == "all":
                data: Any = cursor.fetchall()
            return data

    except sqlite3.Error as e:
        msg = f"{Path(__file__).parts[-1]} {query_db.__name__}() {e}"
        log.error(msg)
        return data


def query_bio(*, date_: date = date.today(), limit: int = 180):
    """Query known streamers to update thieir bio info from website api call"""
    sql = (
        """
        SELECT streamer_name 
        FROM chaturbate 
        WHERE block_date IS NULL 
        AND category IS NOT NULL
        AND IFNULL(bio_chk_date,'1970-01-01') <> ? 
        LIMIT ?
        """,
        (date_, limit),
    )
    data: list[str] = query_db(sql, "all")

    return data


def query_seek_status():
    sql = """
        SELECT streamer_name
        FROM chaturbate
        WHERE block_date IS NULL
        AND seek_capture IS NOT NULL
        AND pid IS NULL
        ORDER BY RANDOM()
        """
    data: list[str] = query_db(sql, "all")

    return data


def query_cap_status(_name: str):
    """Info for determining streamer capture"""
    sql = (
        "SELECT seek_capture, block_date FROM chaturbate WHERE streamer_name = ?",
        (_name,),
    )
    result = query_db(sql)

    return result


def query_url(_name: str):
    sql = (
        "SELECT url_ FROM chaturbate WHERE streamer_name = ?",
        (_name,),
    )
    result = query_db(sql)
    return result


def query_pid(name_: str):
    sql = ("SELECT pid FROM chaturbate WHERE streamer_name = ?", (name_,))
    result: int = query_db(sql)

    return result


def query_capture(value):
    sql = f"SELECT streamer_name, seek_capture, data_total FROM chaturbate WHERE pid IS NOT NULL ORDER BY {value}"
    result = query_db(sql, "all")

    return result


def query_offline(value):
    sql = f"""
        SELECT streamer_name, last_broadcast, data_total 
        FROM chaturbate 
        WHERE pid IS NULL AND seek_capture IS NOT NULL AND block_date IS NULL 
        ORDER BY {value}
        """

    result = query_db(sql, "all")

    return result


def query_long_offline(days: int):
    value = date.today() - timedelta(days=days)
    today_ = date.today()

    sql = (
        """
        SELECT streamer_name 
        FROM chaturbate 
        WHERE (last_broadcast<? or last_broadcast IS NULL)
        AND (bio_chk_date <=? or bio_chk_date IS NULL)
        AND block_date IS NULL
        ORDER BY last_broadcast 
        LIMIT 90

        """,
        (value, today_),
    )
    if not (result := query_db(sql, "all")):
        data = []
        return data

    data: list[str] = [streamer_name for (streamer_name,) in result]

    return data
