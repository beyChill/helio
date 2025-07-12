import inspect
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from enum import StrEnum, auto
from pathlib import Path

import stardust.utils.heliologger as log

BASE_DIR = Path.cwd()


class GetRows(StrEnum):
    FETCHONE = auto()
    FETCHALL = auto()


class HelioDB:
    def __init__(self, db_name: str = "helio", slug=None):
        self.db_name = db_name
        self.slug = slug
        self.conn = None
        self.db_Path = BASE_DIR / "python/stardust/database/db"

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
            PRAGMA journal_mode = OFF;
            PRAGMA temp_store = MEMORY;
            PRAGMA synchronous = OFF;
            PRAGMA locking_mode = exlusive;
            """

        with sqlite3.connect(DB, uri=True) as conn:
            conn.executescript(pragma_query)
            yield conn

    def execute_script(self, sql: str):
        with self.connect_query() as conn:
            cursor = conn.cursor()
            data = cursor.executescript(sql)
            return data

    def execute_query(self, sql: str | tuple, attribute=GetRows.FETCHONE):
        with self.connect_query() as conn:
            cursor = conn.cursor()

            try:
                if not isinstance(sql, tuple):
                    cursor.execute(sql)

                if isinstance(sql, tuple):
                    query, args = sql
                    cursor.execute(query, args)

            except sqlite3.Error as e:
                msg = f"{Path(__file__).parts[-1]} {inspect.stack()[0][3]}() {e}"
                log.error(msg)
                log.error(str(sql))

            return getattr(cursor, attribute)()

    def clean_fetchone(self, sql):
        result = self.execute_query(sql)

        if result and len(result) == 1:
            (tuple_removed,) = result
            return tuple_removed

        return result

    def mfc_query_seek(self):
        sql = f"""
            SELECT streamer_name
            FROM {self.db_name}
            WHERE slug = '{self.slug}'
            AND process_id IS NULL
            """
        seek = set(self.execute_query(sql, GetRows.FETCHALL))
        return seek

    def query_all_db_process_id(self):
        sql = f"""
            SELECT streamer_name, slug, process_id
            FROM {self.db_name}
            WHERE process_id IS NOT NULL
        """
        return self.execute_query(sql, GetRows.FETCHALL)

    def query_url(self, name_, slug):
        sql = (
            f"SELECT capture_url FROM {self.db_name} WHERE streamer_name = ? AND slug = ?",
            (name_, slug),
        )

        return self.clean_fetchone(sql)

    def query_process_id(self, name_, slug):
        sql = (
            f"""
            SELECT process_id
            FROM {self.db_name} 
            WHERE streamer_name = ?
            AND slug = ?
            """,
            (name_, slug),
        )

        return self.clean_fetchone(sql)

    def query_streamers_for_capture(self):
        """Query streamers waiting for capture"""
        sql = f"""
            SELECT streamer_name
            FROM {self.db_name}
            WHERE seek_capture IS NOT NULL
            AND block_date IS NULL
            AND category IS NULL
            AND process_id IS NULL
            AND slug = '{self.slug}'
            """
        data = self.execute_query(sql, GetRows.FETCHALL)
        result = {x for (x,) in data}
        return result

    def query_cap_status(self, name_: str, slug: str):
        """Info for determining streamer capture"""
        sql = (
            f"""
               SELECT seek_capture, block_date
               FROM {self.db_name} 
               WHERE streamer_name = ?
               AND slug = ?
               
               """,
            (name_, slug),
        )
        return self.execute_query(sql)

    def query_active_capture(self, value):
        sql = f"""
            SELECT streamer_name, slug, seek_capture, printf("%.4f", data_total)
            FROM {self.db_name} 
            WHERE process_id IS NOT NULL 
            ORDER BY {value}"""
        result = self.execute_query(sql, GetRows.FETCHALL)

        return result

    def query_seek_offline(self, value):
        sql = f"""
            SELECT streamer_name, slug, last_broadcast, printf("%.4f", data_total) 
            FROM {self.db_name} 
            WHERE process_id IS NULL
            AND seek_capture IS NOT NULL 
            AND block_date ISNULL 
            ORDER BY {value}, streamer_name
            """

        result = self.execute_query(sql, GetRows.FETCHALL)

        return result

    def query_long_offline(self, days: int):
        today_ = date.today()
        value = today_ - timedelta(days=days)

        sql = (
            f"""
            SELECT streamer_name 
            FROM {self.db_name} 
            WHERE (last_broadcast < ? or last_broadcast IS NULL)
            AND (bio_chk_date <= ? or bio_chk_date IS NULL)
            AND block_date IS NULL
            ORDER BY last_broadcast 
            LIMIT 30

            """,
            (value, today_),
        )

        result = self.execute_query(sql, GetRows.FETCHALL)

        data: list[str] = [streamer_name for (streamer_name,) in result]

        return data

    #############################
    # database writes
    #############################

    @contextmanager
    def connect_write(self):
        DB = f"{self.db_Path}/{self.db_name}.sqlite3"

        pragma_write = """
            PRAGMA journal_mode = MEMORY;
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
                    # remove_index = "DROP INDEX IF EXISTS idx_streamer;"
                    # add_index = f"CREATE UNIQUE INDEX IF NOT EXISTS idx_streamer ON {self.db_name} (streamer_name);"

                    conn.execute("BEGIN TRANSACTION")
                    # conn.execute(remove_index)
                    conn.executemany(sql, args)
                    # conn.execute(add_index)
                    conn.execute("END TRANSACTION")

                    conn.executescript("ANALYZE; VACUUM;")
                    return None

                conn.execute(sql, args)

            except sqlite3.Error as e:
                msg = f"{Path(__file__).parts[-1]} {inspect.stack()[0][3]}() {e}"
                log.error(msg)
                log.error(sql)
                # log.error(f"args: {args}")
                log.error(f"{self.slug}")

    def write_not200(self, data: list[tuple]):
        sql = f"""
            INSERT INTO {self.db_name} (streamer_name, slug, http_code, http_text)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (streamer_name, slug)
            DO UPDATE SET
            http_code = EXCLUDED.http_code,
            http_text = EXCLUDED.http_text

            """
        self.execute_write(sql, data)

    def write_seek_capture(self, name_, slug):
        today_ = datetime.now().replace(microsecond=0)
        sql = f"""
            INSERT INTO {self.db_name} (streamer_name, slug, seek_capture) 
            VALUES (?, ?, ?) 
            ON CONFLICT (streamer_name, slug) 
            DO UPDATE SET 
            slug=EXCLUDED.slug,
            seek_capture=EXCLUDED.seek_capture
            WHERE seek_capture ISNULL
            """
        args = (name_, slug, today_)
        self.execute_write(sql, args)

    def write_capture_url(
        self, data: tuple[str, str, str] | list[tuple[str, str, str]]
    ):
        today_ = datetime.now().replace(microsecond=0)
        sql = f"""
            UPDATE {self.db_name}
            SET capture_url = ?,
            last_broadcast = '{today_}'
            WHERE streamer_name = ?
            AND slug = ?
            """

        self.execute_write(sql, data)

    def write_active_capture(
        self,
        data: tuple[int, datetime, str, str] | list[tuple[int, datetime, str, str]],
    ):
        sql = f"""
            UPDATE {self.db_name}
            SET process_id = ?,
            last_capture = ?,
            last_broadcast = last_capture
            WHERE streamer_name = ?
            AND slug = ?
            """

        self.execute_write(sql, data)

    def write_video_size(self, values: tuple[float, str, str]):
        sql = f"""
            UPDATE {self.db_name}
            SET data_total=IFNULL(printf("%.4f", data_total) ,0) + ?
            WHERE streamer_name = ?
            AND slug = ?
            """
        self.execute_write(sql, values)

    def write_null_process_id(self, name_, slug):
        sql = f"""
            UPDATE {self.db_name}
            SET process_id = ?
            WHERE streamer_name = ?
            AND slug = ?
            """
        args = (None, name_, slug)

        self.execute_write(sql, args)

    def write_rm_process_id(self, value: int):
        sql = f"""
            UPDATE {self.db_name}
            SET process_id = ? 
            WHERE process_id = ?
            """

        arg = (None, value)

        self.execute_write(sql, arg)

    def write_rm_seek_capture(self, name_: str, slug: str):
        sql = f"""
            UPDATE {self.db_name}
            SET seek_capture = ?,
            WHERE streamer_name = ?
            AND slug = ?
            """
        args = (None, name_, slug)

        self.execute_write(sql, args)

    def write_last_broadcast(self, streamers: list):
        today_ = datetime.now().replace(microsecond=0)
        sql = f"""
            UPDATE {self.db_name}
            SET last_broadcast = '{today_}'
            WHERE streamer_name = ?
            AND slug = ?                        
            """
        self.execute_write(sql, streamers)

    def write_block_reason(self, data):
        name_, slug, *reason = data
        reason = " ".join(reason)

        sql = f"""
            UPDATE {self.db_name}
            SET block_date = ?,
            seek_capture = ?,
            notes=IFNULL(notes, '') || ?
            WHERE streamer_name = ?
            AND slug =?
            """

        arg = (date.today(), None, f"{reason}", name_, slug)

        self.execute_write(sql, arg)

    def write_data_review(self, value: list[tuple[str, Path]]):
        sql = """
            INSERT INTO {self.db_name} (streamer_name, slug, data_review) 
            VALUES (?, ?, ?) 
            ON CONFLICT (streamer_name, slug) 
            DO UPDATE SET 
            data_review=EXCLUDED.data_review
            """
        self.execute_write(sql, value)

    def write_data_keep(self, value: list[tuple[str, Path]]):
        sql = """
            INSERT INTO {self.db_name} (streamer_name, slug, data_keep) 
            VALUES (?, ?, ?) 
            ON CONFLICT (streamer_name, slug) 
            DO UPDATE SET 
            data_keep=EXCLUDED.data_keep
            """
        self.execute_write(sql, value)
