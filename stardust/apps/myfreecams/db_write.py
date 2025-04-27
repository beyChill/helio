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
    remove_index = "DROP INDEX IF EXISTS idx_num;"
    add_index = (
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_streamer ON chaturbate (streamer_name);"
    )

    with connect_write() as conn:
        # conn.execute(remove_index)
        try:
            conn.execute("BEGIN TRANSACTION")
            conn.executemany(sql, values)
            conn.execute("END TRANSACTION")
        except Exception as e:
            print(e)

        # conn.execute(add_index)
        # 'PRAGMA synchronous = OFF'
        # display_pragma(conn)
        # conn.executescript("ANALYZE; VACUUM;")

# Damn long query. Probably need to spit data from 
# myfreecams api into smaller chuncks. The first 7
# appear related to streaming url
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
    print('data')
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
    print("url")
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
    print("url")
    write_many(sql,values)