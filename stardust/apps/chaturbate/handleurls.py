import asyncio
from random import choice

from rnet import Client, Impersonate, ImpersonateOS, Response

from stardust.apps.chaturbate.models import CBModel, ChatVideoContext, FailVideoContext


class NetActions:
    browser = [Impersonate.Firefox136, Impersonate.Chrome134, Impersonate.Edge131]
    os = [ImpersonateOS.Windows, ImpersonateOS.MacOS, ImpersonateOS.Linux]
    client = Client()

    def __init__(self):
        self.client.update(
            impersonate=choice(self.browser),
        )

    async def get_all_m3u8(self, hls_urls: set[str]):
        tasks = [self.get_m3u8(url) for url in hls_urls]
        results = await asyncio.gather(*tasks)
        return results

    async def get_m3u8(self, url: str):
        resp: Response = await self.client.get(url)
        text_string = await resp.text()
        results = (resp.url, str(text_string))
        return results

    async def get_all_bio(self, streamers: list[str]):
        tasks = [self.get_bio(streamer) for streamer in streamers]
        results = await asyncio.gather(*tasks)
        return results

    async def get_bio(self, streamer: str):
        urls = f"https://chaturbate.com/api/chatvideocontext/{streamer}/"
        resp: Response = await self.client.get(urls)

        if resp.status != 200:
            data = await resp.json()
            fail = FailVideoContext(**data, name_=streamer)
            return fail

        result = ChatVideoContext(**await resp.json())
        return result

    async def get_all_jsons(self, params: str, num_streamers=0) -> list[CBModel]:
        tasks = []
        results = []
        if num_streamers != 0:
            tasks = [
                self.get_json(
                    f"https://chaturbate.com/api/ts/roomlist/room-list/{params}&limit=90&offset={offset}"
                )
                for offset in range(90, num_streamers, 90)
            ]

        if num_streamers == 0:
            tasks = [
                self.get_json(
                    f"https://chaturbate.com/api/ts/roomlist/room-list/{params}&limit=90&offset=0"
                )
            ]

        results = await asyncio.gather(*tasks)
        return results

    async def get_json(self, url: str):
        resp: Response = await self.client.get(url)

        if resp.status != 200:
            return CBModel(rooms=[], total_count=0, all_rooms_count=0, room_list_id="")
        return CBModel(**await resp.json())

    async def get_all_jpg(self, streamers: list[str]):
        tasks = [
            self.get_jpg(f"https://jpeg.live.mmcdn.com/stream?room={streamer}")
            for streamer in streamers
        ]
        return await asyncio.gather(*tasks)

    async def get_jpg(self, url: str):
        resp: Response = await self.client.get(url)
        if resp.status != 200:
            return (resp, None)

        image: bytes = await resp.bytes()
        return (resp, image)

    async def get_ajax_url(self, streamers: list[str]):
        results = []
        tasks = [[("room_slug", name_), ("bandwidth", "high")] for name_ in streamers]

        async with asyncio.TaskGroup() as group:
            for task in tasks:
                task = group.create_task(self.get_ajax(task))
                task.add_done_callback(lambda t: results.append(t.result()))

        return results

    async def get_ajax(self, params):
        base_url = "https://chaturbate.com/get_edge_hls_url_ajax/"
        headers = {"x-requested-with": "XMLHttpRequest"}
        resp: Response = await self.client.post(
            base_url,
            form=params,
            headers=headers,
        )

        data = await resp.json()

        return data
