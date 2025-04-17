from pathlib import Path
import sqlite3
from contextlib import contextmanager
from stardust.config.settings import get_setting
from stardust.utils.applogging import HelioLogger, loglvl

log = HelioLogger()

config = get_setting()

DB_PATH = config.DB_PATH
DB_CONFIG = config.DB_CONFIG


@contextmanager
def connect():
    pragma_initial = """
        PRAGMA auto_vacuum=FULL;
        PRAGMA journal_mode=MEMORY;
        PRAGMA temp_store=MEMORY;
        PRAGMA synchronous=OFF;
        PRAGMA cache_size = 1000000;
        pragma integrity_check;
        PRAGMA optimize; 
        ANALYZE; 
        VACUUM;
        """

    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(pragma_initial)
        yield conn


@contextmanager
def connect_query():
    pragma_query = """
        PRAGMA temp_store = MEMORY;
        PRAGMA synchronous=OFF;
        PRAGMA locking_mode = exlusive;
        """
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(pragma_query)
        yield conn


@contextmanager
def connect_write():
    pragma_write = """
    PRAGMA journal_mode=MEMORY;
    PRAGMA temp_store = MEMORY;
    PRAGMA synchronous=OFF;
    PRAGMA locking_mode = exlusive;
    PRAGMA cache_size = 2000000;
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(pragma_write)
        # if logp.isEnabledFor(PRAG):
        #     # logp.prag("ooooo")
        #     display_pragma(conn)

        yield conn


def db_init() -> None:
    pragma_optimize = "pragma integrity_check; PRAGMA optimize; ANALYZE; VACUUM;"

    if not DB_PATH.is_file():
        log.app(loglvl.CREATED, "Creating database folder")
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        try:
            with connect() as conn:
                with open(DB_CONFIG, "r", encoding="utf-8") as file:
                    conn.executescript(file.read())
                log.app(loglvl.CREATED, "Database inital setup complete")

        except sqlite3.OperationalError as e:
            msg = f"{Path(__file__).parts[-1]} {db_init.__name__}() {e}"
            log.error(msg)

    log.app(loglvl.SUCCESS, "Database is ready")

    # database already active
    with connect() as conn:
        conn.executescript(pragma_optimize)
        # if logp.isEnabledFor(PRAG):
        #     display_pragma(conn)

    return None


def query_db(sql: str | tuple, action: str = "one"):
    data = []
    try:
        with connect_query() as conn:
            cursor = conn.cursor()

            if isinstance(sql, tuple):
                sql_query, args = sql
                cursor.execute(sql_query, args)

            if not isinstance(sql, tuple):
                cursor.execute(sql)

            # if action == "one":
            #     data = cursor.fetchone()

            # if action == "all":
            data = cursor.fetchall()
            return data

    except sqlite3.Error as e:
        msg = f"{Path(__file__).parts[-1]} {query_db.__name__}() {e}"
        log.error(msg)
        return data


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
            print(e)

        conn.execute(add_index)
        # 'PRAGMA synchronous = OFF'
        # display_pragma(conn)
        conn.executescript("ANALYZE; VACUUM;")


def display_pragma(sqlite3_connect):
    pragma_query = [
        "PRAGMA auto_vacuum",
        "PRAGMA journal_mode",
        "PRAGMA temp_store",
        "PRAGMA synchronous",
        "PRAGMA wal_autocheckpoint",
        "PRAGMA cache_size",
        "PRAGMA page_size",
        "PRAGMA mmap_size",
        "PRAGMA cache_spill",
        "PRAGMA locking_mode",
        "PRAGMA integrity_check",
    ]
    for pragma in pragma_query:
        query = sqlite3_connect.execute(pragma)
        for value in query:
            print(pragma, "=", value[0])


if __name__ == "__main__":
    db_init()
