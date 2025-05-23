import asyncio
import time
from random import choice
from typing import Callable

from rnet import Client, Impersonate, Response

from stardust.apps.models_app import not200
from stardust.apps.myfreecams.json_models import (
    Lookup,
    MFCAppModel,
    MfcModelEx,
    Tags,
)
from stardust.utils.applogging import HelioLogger
from stardust.utils.general import filter_not200

log = HelioLogger()

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0"
}


class iNetMfc:
    # Unicode Character in the response will cause print to fail
    # Add the data to a base class prior to printing
    browser = [Impersonate.Firefox136, Impersonate.Chrome134, Impersonate.Edge131]
    client = Client()
    slug = "MFC"

    def __init__(self):
        self.client.update(impersonate=choice(self.browser), headers=headers)

    async def get_user_profile(self, names_: set[str]):
        tasks = {self.get_user(name_) for name_ in names_}
        results = await asyncio.gather(*tasks)

        return filter_not200(results)

    async def get_user(self, name_: str):
        """This endpoint is less likely to return a rate limit with synchronous call

        Run it inside a loop. First 5 or 6 responses are immediate. The remainder
        are ~0.5 seconds or less for each remaining individual request."""
        url = f"https://api-edge.myfreecams.com/usernameLookup/{name_}"

        resp: Response = await self.client.get(url)
        if resp.status != 200:
            return not200(name_=name_, site=self.slug, code_=resp.status, reason=None)

        data = await resp.json()
        if data["result"]["message"] == "user not found":
            return not200(
                name_=name_, site=self.slug, code_=404, reason="user not found"
            )

        if data["result"]["message"] == "servers busy":
            return not200(name_=name_, site=self.slug, code_=413, reason="servers busy")

        return Lookup(**data)

    async def get_all_status(self, names: list[str] | set[str]):
        data = await self.task_group(names, self.get_status)
        new = [Lookup(**x) for x in data]
        return new

    async def get_status(self, name_: str):
        url = f"https://api-edge.myfreecams.com/usernameLookup/{name_}"

        resp: Response = await self.client.get(url)
        if resp.status != 200:
            return not200(name_=name_, site=self.slug, code_=resp.status, reason=None)

        return await resp.json()

    async def get_streamer_app_profile(self, streamers: list[tuple[str, int]]):
        results: list[MFCAppModel | not200]
        tasks = [(name_, uid) for name_, uid in streamers]

        results = await self.task_group(tasks, self.get_streamer)

        return results

    async def get_streamer(self, streamers):
        name_, uid = streamers
        url = f"https://app.myfreecams.com/user/{uid}"
        resp: Response = await self.client.get(url)
        if resp.status != 200:
            return not200(name_=name_, site=self.slug, code_=resp.status, reason=None)

        return MFCAppModel(**await resp.json())

    async def task_group(self, tasks: list | set, func: Callable):
        results = []
        async with asyncio.TaskGroup() as group:
            for task in tasks:
                result = group.create_task(func(task))
                result.add_done_callback(lambda t: results.append(t.result()))

        return filter_not200(results)

    async def get_all_jpg(self, streamers: list[tuple[str, int, int]]):
        """epoch_ is a 13 digit timestamp. Reducing time() to 13 digits."""
        epoch_raw = str(time.time()).replace(".", "")
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
            return (name_, bytes())

        image: bytes = await resp.bytes()
        return (name_, image)

    async def get_model_explorer(self):
        # epoch_ is a 13 digit timestamp. Reducing time() to 13 digits
        epoch_raw = str(time.time()).replace(".", "")
        epoch_ = int(epoch_raw[:-4])

        url = f"https://api-edge.myfreecams.com/modelExplorer/tags?category=tags&order=username&selection=online&limit=1000&full_detail=0&desc=0&search=&expanded=1&_={epoch_}"
        resp: Response = await self.client.get(url)

        result = MfcModelEx(**await resp.json())
        return result

    async def get_tagged_streamers(self):
        """Api providing online streamers having tags. Results are very close to 100%"""
        # epoch_ is a 13 digit timestamp. Reducing time() to 13 digits
        epoch_raw = str(time.time()).replace(".", "")
        epoch_ = int(epoch_raw[:-4])

        url = f"https://api-edge.myfreecams.com/modelExplorer/tags?category=tags&order=username&selection=online&limit=1000&full_detail=0&desc=0&search=&expanded=1&_={epoch_}"
        resp: Response = await self.client.get(url)

        result = Tags(**await resp.json())
        return result
