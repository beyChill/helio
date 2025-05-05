from datetime import date
from stardust.apps.manage_app_db import HelioDB


class DbMfc(HelioDB):
    table_main = "myfreecams"
    table_streamer = "streamer_data"
    table_url = "url_data"

    def query_pid(self, name_:str):
        return self.query_process_id(name_)

    def query_for_img(self):

        """Hard limit of 60 to mimic mfc's cap for img push to clients.
        No rate limit encountered. Trying not to abuse services. """

        time =date.today()
        sql=f"""
            SELECT
                streamer_name, uid_, camserv
            FROM {self.table_url}
            WHERE updated_at > {time}
            ORDER BY RANDOM()
            LIMIT 60
            """
        return self.execute_query(sql,"all")


    def write_seek(self, name_:str):
        return self.write_seek_capture(name_)

    def write_url(self, data: tuple):
        return self.write_capture_url(data)

    def write_urls_all(self, data: list[tuple]):
        return self.write_capture_url(data)
    
    def write_stop_seek(self,name_:str):
        return self.write_rm_seek_capture(name_)

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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (streamer_name)
            DO UPDATE SET
                creation =DATETIME(excluded.creation, 'unixepoch') ,
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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

