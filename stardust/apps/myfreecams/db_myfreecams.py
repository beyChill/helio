from datetime import datetime, timedelta

from stardust.apps.manage_app_db import GetRows, HelioDB


class DbMfc(HelioDB):
    table_main = "myfreecams"
    table_streamer = "streamer_data"
    table_url = "url_data"
    slug = "MFC"

    def query_test_names(self):
        time = datetime.now().replace(microsecond=0) - timedelta(minutes=6)
        sql = f"""
            SELECT streamer_name, camserv, phase, pid, uid_
            FROM {self.table_url}
            WHERE updated_at > '{time}' 
            AND vs = 0
            ORDER BY RANDOM()
            LIMIT 40
            """
        return self.execute_query(sql, GetRows.FETCHALL)

    def query_test_uid(self):
        sql = f"""
            SELECT streamer_name,uid_
            FROM {self.table_url}
            ORDER BY RANDOM()
            LIMIT 50
            """
        return self.execute_query(sql, GetRows.FETCHALL)

    def query_m3u8_data(self, streamers: list[str] | set[str]):
        time = datetime.now().replace(microsecond=0) - timedelta(minutes=6)
        name_ = tuple(streamers)

        arg = f" IN {name_}"

        if len(streamers) < 2:
            # Easier to proceed with a list
            streamers_list = list(streamers)
            arg = f"='{streamers_list[0]}'"

        sql = f"""
            SELECT streamer_name, camserv, phase, pid, uid_
            FROM {self.table_url}
            WHERE streamer_name {arg}
            AND vs = 0
            AND updated_at > '{time}' 
            """

        return self.execute_query(sql, GetRows.FETCHALL)

    def query_uid(self, uid):
        sql = (
            f"""
            SELECT streamer_name
            FROM {self.table_url}
            WHERE uid_ = ?
            
            """,
            (uid,),
        )
        return self.clean_fetchone(sql)

    def query_recent_onlne(self):
        time = datetime.now().replace(microsecond=0) - timedelta(minutes=1)
        sql = f"""
            SELECT streamer_name, uid_, camserv
            FROM {self.table_url}
            WHERE vs=0
            AND updated_at > '{time}'            
            """
        return self.execute_query(sql, GetRows.FETCHALL)

    def query_count_recent_videostate(self):
        time = datetime.now().replace(microsecond=0) - timedelta(minutes=1)
        sql = f"""
            SELECT vs, COUNT(vs)
            FROM {self.table_url}
            WHERE updated_at > '{time}'
            GROUP BY vs 
            ORDER BY COUNT(vs) DESC
            """

        data: list[tuple[int, str]] = self.execute_query(sql, GetRows.FETCHALL)
        return data

    def query_total_recent_videostate(self):
        time = datetime.now().replace(microsecond=0) - timedelta(minutes=1)
        sql = f"""
            SELECT vs, COUNT(vs)
            FROM {self.table_url}
            WHERE updated_at > '{time}'
            """

        data = self.execute_query(sql, GetRows.FETCHALL)
        return data

    def query_for_img(self):
        """Hard limit of 60 to mimic mfc's cap for img push to clients.
        No rate limit encountered. Minimizing stress on server with LIMIT."""

        time = datetime.now().replace(microsecond=0) - timedelta(minutes=7)
        sql = f"""
            SELECT
            streamer_name, uid_, camserv
            FROM {self.table_url}
            WHERE updated_at > '{time}'
            ORDER BY RANDOM()
            LIMIT 60
            """

        return self.execute_query(sql, GetRows.FETCHALL)

    def query_seek_compare(self):
        time = datetime.now().replace(microsecond=0) - timedelta(minutes=3)
        sql = f"""
            SELECT streamer_name
            FROM {self.table_url}
            WHERE updated_at > '{time}'
            and vs = 0
            """
        data = self.execute_query(sql, GetRows.FETCHALL)
        online: set = set(data)

        seek = HelioDB(slug="MFC").query_streamers_for_capture()

        return (online, seek)

    def write_url(self, data: tuple):
        return self.write_capture_url(data)

    def write_urls_all(self, data: list[tuple]):
        return self.write_capture_url(data)

    def write_streamer_data(self, streamer_data):
        sql = f"""
            INSERT INTO {self.table_streamer} (
                streamer_name,
                creation,
                is_new,
                missmfc,
                camscore,
                continent,
                country,
                rank_,
                rc )
            VALUES (LOWER(?), DATETIME(?, 'unixepoch'), ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (streamer_name)
            DO UPDATE SET
                creation =excluded.creation,
                is_new = excluded.is_new,
                missmfc = excluded.missmfc,
                camscore = excluded.camscore,
                continent = excluded.continent,
                country = excluded.country,
                rank_ = excluded.rank_,
                rc = excluded.rc
                """

        return self.execute_write(sql, streamer_data)

    def write_url_data(self, url_data: list):
        sql = f"""
            INSERT INTO {self.table_url} (
                streamer_name,
                sid_,
                uid_,
                vs,
                pid,
                lv,
                camserv,
                phase )
            VALUES (LOWER(?), ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (streamer_name)
            DO UPDATE SET
                sid_ = excluded.sid_,
                uid_ = excluded.uid_,
                vs = excluded.vs,
                pid = excluded.pid,
                lv = excluded.lv ,
                camserv = excluded.camserv,
                phase = excluded.phase
            """

        return self.execute_write(sql, url_data)
