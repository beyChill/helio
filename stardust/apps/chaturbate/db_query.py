from datetime import date

from stardust.database.db_base import query_db


def query_bio(*, date_: date = date.today(), limit: int = 180):
    sql = (
        """
        SELECT streamer_name 
        FROM chaturbate 
        WHERE block_date IS NULL 
        AND capture_status IS NOT NULL
        AND IFNULL(bio_chk_date,'1970-01-01') <> ? 
        LIMIT ?
        """,
        (date_, limit),
    )
    data = query_db(sql)

    return data


def query_capture_status():
    sql = """
        SELECT streamer_name
        FROM chaturbate
        WHERE block_date IS NULL
        AND seek_capture IS NOT NULL
        AND pid IS NULL
        ORDER BY RANDOM()
        """
    data = query_db(sql)

    return data


def query_cap_status(_name: str):
    """Info for determining streamer capture"""
    sql = (
        "SELECT seek_capture, block_date FROM chaturbate WHERE streamer_name=?",
        (_name,),
    )
    result = query_db(sql)

    return result


def query_url(_name: str):
    sql = (
        "SELECT url_ FROM chaturbate WHERE streamer_name=?",
        (_name,),
    )
    result = query_db(sql)
    return result


def query_pid(_name: str):
    sql = (
        "SELECT pid FROM chaturbate WHERE streamer_name=?",
        (_name,),
    )
    result = query_db(sql)
    return result
