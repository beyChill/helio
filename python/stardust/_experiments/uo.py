import asyncio
from rnet import Client, Impersonate, ImpersonateOption, Response


async def chk():
    try:
        # browser = ImpersonateOption.random()
        url = "http://httpbin.org/headers"
        tls = "https://tls.peet.ws/api/all"
        resp: Response = await Client().get(url)
        resp_tls: Response = await Client().get(tls)
        
        ua = await resp.json()
        ua_tls = await resp_tls.json()
        print(ua)
        print(ua_tls)
        print("url:", ua["headers"]["User-Agent"])
        print("tls:", ua_tls["user_agent"])

    except Exception as e:
        print(e)


for _ in range(1):
    asyncio.run(chk())
