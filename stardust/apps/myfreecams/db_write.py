from contextlib import contextmanager
import sqlite3

from stardust.config.settings import get_db_setting

@contextmanager
def connect_write():
    DB = get_db_setting().MFC_DB_FOLDER

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

# removed index to speed writes.  However adding time back 
# when attempting write in a different table is a problem.
def write_many(sql: str, values):
    remove_index = "DROP INDEX IF EXISTS idx_streamer;"
    add_index = (
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_streamer ON myfreecams (streamer_name);"
    )

    with connect_write() as conn:
        try:
            conn.execute("BEGIN TRANSACTION")
            conn.execute(remove_index)
            conn.executemany(sql, values)
            conn.execute(add_index)
            conn.execute("END TRANSACTION")
        except Exception as e:
            print(e)

        # 'PRAGMA synchronous = OFF'
        # display_pragma(conn)
        conn.executescript("ANALYZE; VACUUM;")

def streamers_online(values,url_data):
    
    sql = """
        INSERT INTO myfreecams (
            streamer_name,
            creation,
            is_new,
            missmfc,
            camscore,
            continent,
            country,
            rank_,
            rc )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (streamer_name)
        DO UPDATE SET
            creation = excluded.creation,
            is_new = excluded.is_new,
            missmfc = excluded.missmfc,
            camscore = excluded.camscore,
            continent = excluded.continent,
            country = excluded.country,
            rank_ = excluded.rank_,
            rc = excluded.rc,
            last_broadcast = DATETIME('now', 'localtime')
            """

    write_many(sql,values)

    sql2 = """
        INSERT INTO url_data (
            streamer_name,
            sid,
            uid,
            vs,
            pid,
            lv,
            camserv,
            phase )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (streamer_name)
        DO UPDATE SET
            sid = excluded.sid,
            uid = excluded.uid,
            vs = excluded.vs,
            pid = excluded.pid,
            lv = excluded.lv ,
            camserv = excluded.camserv,
            phase = excluded.phase
        """

    write_many(sql2,url_data)

def streamers_url_data(values):
    sql = """
        INSERT INTO url_data (
            streamer_name,
            sid,
            uid,
            vs,
            pid,
            lv,
            camserv,
            phase )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (streamer_name)
        DO UPDATE SET
            sid = excluded.sid,
            uid = excluded.uid,
            vs = excluded.vs,
            pid = excluded.pid,
            lv = excluded.lv ,
            camserv = excluded.camserv,
            phase = excluded.phase
        """

    write_many(sql,values)