import asyncio
from random import choice

from rnet import Client, Impersonate, Response

from stardust.apps.myfreecams.models_mfc import MFCModel

class MfcNetActions:
    browser = [Impersonate.Firefox136, Impersonate.Chrome134, Impersonate.Edge131]
    client = Client()

    def __init__(self):
        self.client.update(
            impersonate=choice(self.browser),
        )

    async def get_user_profile(self, names_: list[str]):
        tasks = [self.get_user(name_) for name_ in names_]
        results = await asyncio.gather(*tasks)
        result = [x for x in results if x]
        return result

    async def get_user(self, name_: str):
        url = f"https://api-edge.myfreecams.com/usernameLookup/{name_}"
        resp: Response = await self.client.get(url)
        if resp.status != 200:
            print(name_,resp.status,await resp.text())
            return 
        
        result = MFCModel(**await resp.json())
        return result
