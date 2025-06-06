from random import choice

import m3u8
from rnet import Client, Impersonate, Response

import stardust.utils.heliologger as log

class HandleM3u8:
    url: str
    text: str
    urls = set()
    client = Client()
    browser = [
        Impersonate.Chrome136,
        Impersonate.Edge134,
        Impersonate.Firefox136,
        Impersonate.Safari18,
    ]

    def __init__(self, url: str):
        self.client.update(impersonate=choice(self.browser))
        self.url = url

    async def get_playlist(self):
        resp: Response = await self.client.get(self.url)

        # Each site's response to 400 series codes is different.
        # Need site specific handlers, which is activated by
        # a return value of None
        if resp.status in [403, 404]:
            return

        if resp.status != 200:
            log.failure(f"HandleM3u8: {resp.status} {self.url}")
            return

        self.text = await resp.text()
        return self.text

    def get_m3u8(self):
        self.m3u8 = self.load()
        self.top_bandwidth = self.get_top_bandwidth()
        return self.top_bandwidth

    def load(self):
        text_ = m3u8.loads(self.text)
        return text_

    def get_top_bandwidth(self):
        if not self.m3u8.is_variant:
            log.error("Encountered a problem with the m3u8")
            return self.url

        top_bw = max(
            self.m3u8.playlists,
            key=lambda x: x.stream_info.bandwidth
            if isinstance(x.stream_info.bandwidth, int)
            else False,
        )

        if top_bw.uri is None:
            return self.url

        return top_bw.uri

    async def cb_m3u8(self):
        if await self.get_playlist() is None:
            return
        bw = self.get_m3u8()
        new_m3u8: str = self.url.replace("playlist.m3u8", str(bw))
        streamer_name: str = new_m3u8.rsplit("-sd-")[0].split("amlst:")[1]
        return (new_m3u8, streamer_name, str("CB"))

    async def mfc_m3u8(self):
        if await self.get_playlist() is None:
            return
        bw = self.get_m3u8()
        split_m3u8 = self.url.split("/").pop()
        new_url = self.url.replace(split_m3u8, str(bw))
        return new_url
