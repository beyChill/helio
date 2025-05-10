import traceback
from typing import Optional
import m3u8

from stardust.utils.applogging import HelioLogger

log = HelioLogger()


class HandleM3u8:
    url: str
    text: str

    def __init__(self, data: tuple):
        self.url, self.text = data
        self.m3u8 = self.load()

        self.top_bandwidth = self.get_top_bandwidth()

    def load(self):
        data = m3u8.loads(self.text)
        return data

    def get_top_bandwidth(self):
        if not self.m3u8.is_variant:
            log.error("m3u8 playlist is invalid")
            return

        top_bw = max(
            self.m3u8.playlists,
            key=lambda x: x.stream_info.bandwidth
            if isinstance(x.stream_info.bandwidth, int)
            else False,
        )
        return top_bw.uri

    def cb_m3u8(self):
        new_m3u8: str = self.url.replace("playlist.m3u8", str(self.top_bandwidth))
        streamer_name: str = new_m3u8.rsplit("-sd-")[0].split("amlst:")[1]
        return (new_m3u8, streamer_name)

    def mfc_m3u8(self):
        split_m3u8 = self.url.split("/").pop()
        new_url = self.url.replace(split_m3u8, str(self.top_bandwidth))
        return new_url
