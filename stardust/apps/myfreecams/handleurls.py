import asyncio
import time
from random import choice
from typing import Callable

from rnet import Client, Impersonate, Response

from stardust.apps.myfreecams.models_mfc import GetStreamerResult, MFCAppModel, MFCModel
from stardust.utils.applogging import HelioLogger

log = HelioLogger()


class MfcNetActions:
    browser = [Impersonate.Firefox136, Impersonate.Chrome134, Impersonate.Edge131]
    client = Client()

    def __init__(self):
        self.client.update(
            impersonate=choice(self.browser),
        )

    async def get_user_profile(self, names_: list[str]):
        tasks = [self.get_user(name_) for name_ in names_]
        all_results = await asyncio.gather(*tasks)
        results = [result for result in all_results if result]
        return results

    async def get_user(self, name_: str):
        url = f"https://api-edge.myfreecams.com/usernameLookup/{name_}"

        resp: Response = await self.client.get(url)
        if resp.status != 200:
            log.error(f"{name_}: {resp.status}, {await resp.text()}")
            return

        result = MFCModel(**await resp.json())
        return result

    async def get_streamer_app_profile(self, streamers: list[tuple[str, int]]):
        data: list[GetStreamerResult] = []
        tasks = [(name_, uid) for name_, uid in streamers]

        data = await self.task_group(tasks, self.get_streamer)

        results = [result for result in data if result.status == 200]
        return results

    async def get_streamer(self, name_, uid):
        url = f"https://app.myfreecams.com/user/{uid}"
        resp: Response = await self.client.get(url)
        if resp.status != 200:
            log.error(
                f"{resp.status}: rate Limit for {name_}",
            )
            return GetStreamerResult(name_=name_, data=None, status=resp.status)
        result = GetStreamerResult(
            name_=name_, data=MFCAppModel(**await resp.json()), status=resp.status
        )
        return result

    async def task_group(self, tasks: list, func: Callable):
        results = []
        async with asyncio.TaskGroup() as group:
            for task in tasks:
                task = group.create_task(func(*task))
                task.add_done_callback(lambda t: results.append(t.result()))

        return results

    async def get_all_m3u8(self, hls_urls: list[str]):
        tasks = [self.get_m3u8(url) for url in hls_urls]
        results = await asyncio.gather(*tasks)
        return results

    async def get_m3u8(self, url: str):
        resp: Response = await self.client.get(url)
        results = await resp.text()
        return results

    async def get_all_jpg(self, streamers: list[tuple[str, int, int]]):
        """final url parameter is a 13 digit timestamp. Reducing time() to 13 digits."""
        epoch_raw = str(time.time()).replace(".","")
        epoch_ = int(epoch_raw[:-4])

        tasks = [
            self.get_jpg(
                (
                    name_,
                    f"https://snap.mfcimg.com/snapimg/{server}/853x480/mfc_{id}?no-cache={epoch_}",
                )
            )
            for name_, server, id in streamers
        ]

        return await asyncio.gather(*tasks)

    async def get_jpg(self, data: tuple[str, str]):
        name_, url = data
        resp: Response = await self.client.get(url)
        if resp.status != 200:
            print(name_, resp.status_code)
            return (name_, bytes())

        image: bytes = await resp.bytes()
        return (name_, image)
