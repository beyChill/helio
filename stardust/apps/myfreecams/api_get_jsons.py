import asyncio
import json
from pathlib import Path
from random import choice
from threading import Thread

import pandas as pd
from mitmproxy import addons, ctx, http
from mitmproxy.http import HTTPFlow
from mitmproxy.master import Master
from mitmproxy.options import Options
from seleniumbase import SB

from stardust.apps.myfreecams.db_myfreemcams import DbMfc
import stardust.utils.heliologger  as log
from stardust.utils.general import script_delay
from stardust.utils.timer import AppTimerSync

# BLOCK_WORDS and BLOCK_EXTENSIONS limit the reponses handled by mitmproxy
BLOCK_WORDS = [
    "assets",
    "favicon",
    "google",
    "google-analytics",
    "mobile",
    "snap.mfcimg",
]

BLOCK_EXTENSIONS = [
    ".gif",
    ".jpg",
    ".jpeg",
    ".js",
    ".png",
    ".svg",
    ".webp",
]


class AppDirs:
    def __init__(self):
        self.base = self._find_base_dir()
        self.certs = self._create_mitm_dir()
        self.data = self._create_data_dir()

    def _find_base_dir(self):
        home = Path("~/")
        base = Path.expanduser(home)
        return base

    def _create_mitm_dir(self):
        certs = Path(self.base / ".helio/mitmproxy")
        certs.mkdir(parents=True, exist_ok=True)
        return certs

    def _create_data_dir(self):
        data = Path(self.base / ".helio/data")
        data.mkdir(parents=True, exist_ok=True)
        return data

    def base_dir(self):
        return self.base

    def mitm_dir(self):
        return self.certs

    def data_dir(self):
        return self.data


class AppRequest:
    def __init__(self):
        pass

    def request(self, flow: http.HTTPFlow) -> None:
        del flow.request.headers["accept-encoding"]
        flow.request.headers["accept-encoding"] = "gzip"
        url = flow.request.pretty_url

        if url.__contains__("playlist"):
            log.info(f"Request: {url}")

        block_extension = any(url.endswith(ext) for ext in BLOCK_EXTENSIONS)
        block_words = any(block in url for block in BLOCK_WORDS)

        if block_extension or block_words:
            return


class AppResponse:
    def response(self, flow: http.HTTPFlow) -> None:
        url = flow.request.pretty_url

        if url.__contains__("playlist"):
            log.info(f"response: {url}")

        if url.endswith("debug=cams"): 
            handle_streamers_online(flow)
            return


def handle_streamers_online(flow: HTTPFlow):
    db = DbMfc("myfreecams")
    if flow.response is None:
        return

    if (body := flow.response.text) is None:
        return

    json_ = json.loads(body)
    log.query(f"{json_['count']} MFC streamers online")
    data = json_["rdata"]
    df = pd.DataFrame((data[1:]))

    # Not sure of simple method to include all data from api (63 columns)
    # keeping most valuable colums vs all columns
    df_url = df.iloc[:, :8]
    url_data: list = df_url.values.tolist()

    # Again just keeping valued data from the 63 items the api provides
    other_data = df.loc[0:, [0, 11, 16, 17, 18, 19, 20, 21, 22]]

    # the dataframe to sql function (tosql) overwrites column heads in table.
    # converting it to a list eliminates issue.
    streamer_data: list = other_data.values.tolist()

    db.write_streamer_data(streamer_data)
    db.write_url_data(url_data)

    return None


class MitmServer:
    def __init__(self):
        self.ip_address = None
        self._ssl_insecure = True
        self._thread_loop()
        self._master_proxy()
        asyncio.run(self.start())
        super().__init__()

    def _master_proxy(self):
        opts = Options()
        Master(opts, self.loop)
        handlers = [*addons.default_addons(), AppResponse(), AppRequest()]
        _ = [ctx.master.addons.add(handle) for handle in handlers]

        opts.update(
            confdir=str(AppDirs().mitm_dir()),
            listen_host="localhost",
            listen_port=0,
            ssl_insecure=True,
        )

    def _thread_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        thread = Thread(target=self.loop.run_forever, daemon=True)
        thread.start()

    def _has_proxy_address(self):
        if not (ipaddress := ctx.master.addons.lookup["proxyserver"].listen_addrs()):
            return None

        if len(ipaddress[0]) == 2:
            addr, port = ipaddress[0]
            self.ip_address = f"{addr}:{port}"
            return self.ip_address

        addr, port = ipaddress[1]
        self.ip_address = f"{addr}:{port}"

        # Seleniumbase using Chrome browser doesn't support IPv6 Proxy/
        # Review SeleniumBase's code, GitHub: SeleniumBase / seleniumbase / core / proxy_helper.py
        # Selenium supports IPv6. Leaving the code just incase seleniumbase is not a solution.

        # addr, port, *_ = ipaddress[0]
        # self.ip_address = f"[{addr}]:{port}"

        return self.ip_address

    async def start(self):
        asyncio.run_coroutine_threadsafe(ctx.master.run(), self.loop)

        # mitmproxy needs an instance in time to start
        while not self._has_proxy_address():
            await asyncio.sleep(0.009)

    @property
    def proxy_address(self):
        return self.ip_address


@AppTimerSync
def launch_sb_for_mfc(proxy):
    """
    Launch seleniumbase on myfreecams.com
    MyFreeCams api sends a json containing all online
    streamers. The api auto generates online streamer
    data. This data return is easier and has more reliable
    access vs generating a http get request for this specific
    data. Manually creating the api request is not straight forward.
    """

    # add these args to view (unhide) the web brower
    headed = True
    headless2 = (False,)

    window_position = f"{choice(range(401, 912))},{choice(range(321, 863))}"
    window_size = f"{choice(range(601, 1011))}, {choice(range(122, 643))}"

    if not headed and headless2:
        window_position = f"{choice(range(101, 412))},{choice(range(121, 563))}"
        window_size = f"{choice(range(201, 311))}, {choice(range(222, 343))}"

    with SB(
        uc=True,
        locale="en",
        proxy=proxy,
        headed=headed,
        headless2=headless2,
        window_size=(f"{window_size}"),
        window_position=window_position,
    ) as sb:
        url = "https://www.myfreecams.com"
        sb.activate_cdp_mode(url)

        # delay for myfreecams api to respond,api seems a bit slow
        # refactor to probably recieve a site trigger.
        asyncio.run(asyncio.sleep(2))


@AppTimerSync
def mitm_init():
    init_ = MitmServer()
    launch_sb_for_mfc(init_.proxy_address)


async def get_mfc_online_json():
    # mitmproxy requires and event loop. It is simplier to
    # give the proxy it's own event loop in a separate thread.
    # Allowing for the inital to run forever as a means
    # to continually query myfreecams for data.

    while True:
        thread = Thread(target=mitm_init, daemon=True)
        thread.start()
        thread.join()

        delay_, time_ = script_delay(309.07, 425.89)
        log.query(f"MFC streamers @: {time_}")
        await asyncio.sleep(delay_)


def exception_handler(loop, context) -> None:
    log.error(context["exception"])
    log.error(context["message"])


def loop_mfc_all_online():
    loop = asyncio.new_event_loop()
    # loop.set_exception_handler(exception_handler)
    loop.create_task(get_mfc_online_json())
    loop.run_forever()


if __name__ == "__main__":
    loop_mfc_all_online()
