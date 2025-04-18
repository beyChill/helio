from datetime import date, timedelta

from stardust.database.db_base import query_db


def query_bio(*, date_: date = date.today(), limit: int = 180):
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
    data = query_db(sql, "all")

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
    data = query_db(sql, "all")

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

    print("querying:", today_, value)
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
