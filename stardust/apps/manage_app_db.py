from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path
import sqlite3
from typing import Any

from pydantic import HttpUrl

from stardust.utils.applogging import HelioLogger
import inspect


BASE_DIR = Path.cwd()

log = HelioLogger()


class HelioDB:
    def __init__(self, db_name: str, **kwargs):
        self.db_name = db_name
        self.conn = None
        self.db_Path = BASE_DIR / "stardust/database/db"

    #############################
    # database queries
    #############################

    @contextmanager
    def connect_query(self):
        # URI options require path prefix 'file:'.  Windows has more requirements
        # see:  https://www.sqlite.org/uri.html section 3.1
        # using immutable for performance gain
        DB = f"file:{self.db_Path}/{self.db_name}.sqlite3?immutable=1"

        pragma_query = """
            PRAGMA journal_mode=OFF;
            PRAGMA temp_store=MEMORY;
            PRAGMA synchronous=OFF;
            PRAGMA locking_mode=exlusive;
            """

        with sqlite3.connect(DB, uri=True) as conn:
            conn.executescript(pragma_query)
            yield conn

    def execute_query(self, sql: str | tuple, fetch: str = "one"):
        data: Any = ()
        with self.connect_query() as conn:
            try:
                cursor = conn.cursor()

                if not isinstance(sql, tuple):
                    cursor.execute(sql)

                if isinstance(sql, tuple):
                    query, args = sql
                    cursor.execute(query, args)

                if fetch == "one":
                    data = cursor.fetchone()

                if fetch == "all":
                    data = cursor.fetchall()

                return data
            except sqlite3.Error as e:
                msg = f"{Path(__file__).parts[-1]} {inspect.stack()[0][3]}() {e}"
                log.error(msg)
                log.error(str(sql))

    def clean_fetchone(self, sql):
        test_variable = None

        result = self.execute_query(sql)

        if result and len(result) == 1:
            (test_variable,) = result
            return test_variable

        return result

    def query_url(self, name_):
        sql = (
            f"SELECT capture_url FROM {self.db_name} WHERE streamer_name = ?",
            (name_,),
        )
        result = self.clean_fetchone(sql)

        if not result:
            return None

        link: HttpUrl = result
        return link

    def query_process_id(self, name_):
        sql = (
            f"SELECT process_id FROM {self.db_name} WHERE streamer_name = ?",
            (name_,),
        )
        # if not result:
        return self.clean_fetchone(sql)

    def query_seek_capture(self):
        sql = f"""
            SELECT streamer_name, seek_capture
            FROM {self.db_name}
            WHERE block_date IS NULL
            AND seek_capture IS NOT NULL
            AND process_id IS NULL
            ORDER BY RANDOM()
            """
        data = self.execute_query(sql, "all")

        return data

    def query_main_streamers(self):
        sql = f"""
            SELECT streamer_name, seek_capture
            FROM {self.db_name}
            WHERE block_date IS NULL
            AND category IS NULL
            AND process_id IS NULL
            ORDER BY RANDOM()
            """
        data = self.execute_query(sql, "all")

        return data

    def query_cap_status(self, name_: str):
        """Info for determining streamer capture"""
        sql = (
            f"SELECT seek_capture, block_date FROM {self.db_name} WHERE streamer_name = ?",
            (name_,),
        )
        return self.clean_fetchone(sql)

    def query_active_capture(self, value):
        sql = f"""
            SELECT streamer_name, seek_capture, printf("%.4f", data_total)
            FROM {self.db_name} 
            WHERE process_id IS NOT NULL 
            ORDER BY {value}"""
        result = self.execute_query(sql, "all")

        return result

    def query_seek_offline(self, value):
        sql = f"""
            SELECT streamer_name, last_broadcast, printf("%.4f", data_total) 
            FROM {self.db_name} 
            WHERE process_id IS NULL
            AND seek_capture IS NOT NULL 
            AND block_date IS NULL 
            ORDER BY {value}
            """

        result = self.execute_query(sql, "all")

        return result

    def query_long_offline(self, days: int):
        value = date.today() - timedelta(days=days)
        today_ = date.today()

        sql = (
            f"""
            SELECT streamer_name 
            FROM {self.db_name} 
            WHERE (last_broadcast<? or last_broadcast IS NULL)
            AND (bio_chk_date <=? or bio_chk_date IS NULL)
            AND block_date IS NULL
            ORDER BY last_broadcast 
            LIMIT 30

            """,
            (value, today_),
        )

        if not (result := self.execute_query(sql, "all")):
            return []

        data: list[str] = [streamer_name for (streamer_name,) in result]

        return data

    #############################
    # database writes
    #############################

    @contextmanager
    def connect_write(self):
        DB = f"{self.db_Path}/{self.db_name}.sqlite3"

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

    # @AppTimerSync
    def execute_write(self, sql: str, args: tuple | list = []):
        with self.connect_write() as conn:
            try:
                if isinstance(args, list):
                    remove_index = "DROP INDEX IF EXISTS idx_streamer;"
                    add_index = f"CREATE UNIQUE INDEX IF NOT EXISTS idx_streamer ON {self.db_name} (streamer_name);"

                    conn.execute("BEGIN TRANSACTION")
                    conn.execute(remove_index)
                    conn.executemany(sql, args)
                    conn.execute(add_index)
                    conn.execute("END TRANSACTION")

                    conn.executescript("ANALYZE; VACUUM;")
                    return None

                conn.execute(sql, args)

            except sqlite3.Error as e:
                msg = f"{Path(__file__).parts[-1]} {inspect.stack()[0][3]}() {e}"
                log.error(msg)
                log.error(sql)
                log.error(f"{args}")

    def write_seek_capture(self, name_):
        today_ = datetime.now().replace(microsecond=0)
        sql = f"""
            INSERT INTO {self.db_name} (streamer_name, seek_capture) 
            VALUES (?, ?) 
            ON CONFLICT (streamer_name) 
            DO UPDATE SET 
            seek_capture=EXCLUDED.seek_capture
            WHERE seek_capture IS NULL
            """
        args = (name_, today_)
        self.execute_write(sql, args)

    def write_capture_url(self, data: tuple[str, str] | list[tuple[str, str]]):
        sql = f"""
            UPDATE {self.db_name}
            SET capture_url= ?
            WHERE streamer_name = ?
            """
        self.execute_write(sql, data)

    def write_process_id(
        self, data: tuple[int, datetime, str] | list[tuple[int, datetime, str]]
    ):
        sql = f"""
            UPDATE {self.db_name}
            SET 
            process_id = ?,
            last_capture= ?
            WHERE streamer_name = ?
            """

        self.execute_write(sql, data)

    def write_video_size(self, values: tuple[float, str]):
        sql = f"""
            UPDATE {self.db_name}
            SET data_total=IFNULL(printf("%.4f", data_total) ,0) + ?
            WHERE streamer_name = ?
            """

        self.execute_write(sql, values)

    def write_rm_process_id(self, value: int):
        sql = f"UPDATE {self.db_name} SET process_id = ? WHERE process_id = ?"
        self.execute_write(sql, (None, value))

    def write_rm_seek_capture(self, name_: str):
        sql = f"UPDATE {self.db_name} SET seek_capture=?, process_id=? WHERE streamer_name=?"
        args = (None, None, name_)

        self.execute_write(sql, args)

    def write_last_broadcast(self, streamers: list):
        today_ = datetime.now().replace(microsecond=0)
        sql = f"""
            UPDATE {self.db_name}
            SET last_broadcast = '{today_}'
            WHERE streamer_name = ?                        
            """
        self.execute_write(sql, streamers)

    def write_block_reason(self, data):
        name_, *reason = data
        reason = " ".join(reason)

        sql = f"""
            UPDATE {self.db_name}
            SET block_date=?, seek_capture=?, notes=IFNULL(notes, '')||?
            WHERE streamer_name=?
            """

        arg = (date.today(), None, f"{reason}", name_)

        self.execute_write(sql, arg)
