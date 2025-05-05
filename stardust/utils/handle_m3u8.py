from urllib.error import HTTPError

import m3u8

from stardust.utils.applogging import HelioLogger

log = HelioLogger()


class HandleM3u8:
    def __init__(self, url: str):
        self.url = url
        self.m3u8 = self.load()

        if not self.m3u8:
            return

        self.top_bandwidth = self.get_top_bandwidth()
        self.cb_m3u8 = self.new_cb_m3u8()
        self.mfc_m3u8 = self.new_mfc_m3u8()

    def load(self):
        data = ""
        try:
            data = m3u8.load(self.url)
            return data
        except HTTPError as e:
            log.warning(f"{e}")
            return None

    def get_top_bandwidth(self):
        if not self.m3u8:
            return

        top_bw = max(
            self.m3u8.playlists,
            key=lambda x: x.stream_info.bandwidth
            if isinstance(x.stream_info.bandwidth, int)
            else False,
        )
        return top_bw.uri

    def new_cb_m3u8(self):
        new_m3u8 = self.url.replace("playlist.m3u8", str(self.top_bandwidth))
        return new_m3u8

    def new_mfc_m3u8(self):
        split_m3u8 = self.url.split("/").pop()
        new_url = self.url.replace(split_m3u8, str(self.top_bandwidth))
        return new_url
