from datetime import date

from stardust.apps.chaturbate.models import FailVideoContext
from stardust.apps.manage_app_db import GetRows, HelioDB


class DbCb(HelioDB):
    table_main = "chaturbate"
    table_streamer = "streamer_data"

    def query_bio(self, *, date_: date = date.today(), limit: int = 180):
        """Query known streamers to update thier bio info from website api call"""
        sql = (
            f"""
            SELECT streamer_name 
            FROM {self.table_streamer}
            WHERE IFNULL(bio_chk_date,'1970-01-01') <> ? 
            LIMIT ?
            """,
            (date_, limit),
        )
        data = self.execute_query(sql, GetRows.FETCHALL)

        return data

    def write_url(self, data: tuple):
        return self.write_capture_url(data)

    def write_urls_all(self, data: list[tuple]):
        return self.write_capture_url(data)

    def write_api_data(self, value: list):
        sql = f"""
            INSERT INTO {self.table_streamer} (
            streamer_name, age, last_broadcast, viewers, tags)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (streamer_name)
            DO UPDATE SET
            age=EXCLUDED.age,
            last_broadcast=IFNULL(last_broadcast, EXCLUDED.last_broadcast),
            viewers=EXCLUDED.viewers,
            most_viewers=MAX(most_viewers, EXCLUDED.viewers),
            tags=EXCLUDED.tags,
            bio_chk_date=DATE('now', 'localtime');
            """

        self.execute_write(sql, value)

    def write_db_streamers(self, value: list):
        sql = f"""
            INSERT INTO {self.table_streamer} (
            streamer_name, age, last_broadcast, followers, viewers,start_dt_utc, location, country, is_new, tags,bio_chk_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (streamer_name)
            DO UPDATE SET 
            age=EXCLUDED.age,
            last_broadcast=EXCLUDED.last_broadcast,
            followers=EXCLUDED.followers,
            viewers=EXCLUDED.viewers,
            start_dt_utc=EXCLUDED.start_dt_utc,
            most_viewers=MAX(most_viewers, EXCLUDED.viewers),
            location=EXCLUDED.location,
            country=EXCLUDED.country,
            is_new=EXCLUDED.is_new,
            tags=EXCLUDED.tags,
            bio_chk_date=EXCLUDED.bio_chk_date
            """
        self.execute_write(sql, value)

    def write_videocontext_fail(self, values: set[FailVideoContext]):
        data = []
        for value in values:
            data.append((value.status, value.detail, value.code, value.name_))
        sql = f"""
            UPDATE {self.table_streamer}
            SET bio_chk_date=DATETIME('now', 'localtime'),
            bio_fail_date=DATETIME('now', 'localtime'),
            bio_fail_status=?,
            bio_fail_detail=?,
            bio_fail_code=?
            WHERE streamer_name=?
            """

        self.execute_write(sql, data)
