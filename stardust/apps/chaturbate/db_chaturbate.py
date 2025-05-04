from stardust.apps.manage_app_db import HelioDB

class DbCb(HelioDB):
    table_main = "chaturbate"
    table_streamer = "streamer_data"

    def query_pid(self, name_):
        return self.query_process_id(name_)

    def write_seek(self, name_):
        return self.write_seek_capture(name_)

    def write_url(self, data: tuple):
        return self.write_capture_url(data)

    def write_urls_all(self, data: list[tuple]):
        return self.write_capture_url(data)

    def write_stop_seek(self,name_:str):
        return self.write_rm_seek_capture(name_)