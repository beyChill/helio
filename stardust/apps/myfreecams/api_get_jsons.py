import asyncio
import json
import time
from random import choice
from threading import Thread

import pandas as pd
from mitmproxy import addons, ctx, http
from mitmproxy.http import HTTPFlow
from mitmproxy.master import Master
from mitmproxy.options import Options
from seleniumbase import SB

from stardust.apps.myfreecams.db_myfreemcams import DbMfc
from stardust.config.settings import get_setting
from stardust.utils.applogging import HelioLogger
from stardust.utils.general import script_delay
from stardust.utils.timer import AppTimerSync

log = HelioLogger()
dir_ = get_setting()

BLOCK_WORDS = [
    "assets",
    "favicon",
    "google",
    "google-analytics",
    "mobile",
    "snap.mfcimg",
    "gstatic",
    "gvt1",
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


class MFCaddon:
    def request(self, flow: http.HTTPFlow) -> None:
        del flow.request.headers["accept-encoding"]
        flow.request.headers["accept-encoding"] = "gzip"

    def response(self, flow: http.HTTPFlow) -> None:
        url = flow.request.pretty_url
        block_extension = any(url.endswith(ext) for ext in BLOCK_EXTENSIONS)
        block_words = any(block in url for block in BLOCK_WORDS)

        if block_extension or block_words:
            return

        if url.endswith("debug=cams"):
            handle_streamers_online(flow)
            return


class Proxy(Thread):
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.local_host = "127.0.0.1"
        self.port = 0
        self.config()
        super().__init__()

    def config(self):
        opts = Options(
            confdir=str(dir_.DIR_MITM_CONFIG),
            # setting local host to IPv4 prevents
            # generation of IPv6 address
            listen_host=self.local_host,
            # listen_port=0 instructs mitmproxy to select
            # a random available port,
            listen_port=0,
            ssl_insecure=True,
        )
        Master(opts, self.loop)
        handlers = [*addons.default_addons(), MFCaddon()]
        _ = {ctx.master.addons.add(handle) for handle in handlers}

    def run(self) -> None:
        self.loop.run_until_complete(ctx.master.run())

    def get_port(self):
        _, self.port = ctx.master.addons.lookup["proxyserver"].listen_addrs()[0]

    def stop_server(self):
        # server is enabled by default via the
        # mitmproxy import of Options()
        ctx.options.update(server=False)

    def __enter__(self):
        # start is from threading.Thread, it will triggers the run method
        self.start()
        time.sleep(0.009)
        self.get_port()
        return self

    def __exit__(self, *_) -> None:
        ctx.master.event_loop.call_soon_threadsafe(self.stop_server)
        ctx.master.shutdown()
        self.join()
        self.loop.close()

    @property
    def proxy_address(self):
        sb_proxy = f"{self.local_host}:{self.port}"
        return sb_proxy


@AppTimerSync
def launch_sb_for_mfc(sb_proxy):
    """
    Launch seleniumbase on myfreecams.com
    MyFreeCams api sends a json containing all online
    streamers. The api auto generates online streamer
    data. This data returned is easier and has more reliable
    access vs generating a http get request for this specific
    data. Manually creating the api request is not straight forward.
    """

    # change these args to view (unhide) the web brower
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
        proxy=sb_proxy,
        headed=headed,
        headless2=headless2,
        window_size=(f"{window_size}"),
        window_position=window_position,
    ) as sb:
        url = "https://www.myfreecams.com"
        sb.activate_cdp_mode(url)

        # delay for myfreecams api to provide json data.
        # TODO: terminate SeleniumBase after desired data is received.
        asyncio.run(asyncio.sleep(2))


def mitm_init():
    with Proxy() as mitm:
        proxy_address = mitm.proxy_address
        launch_sb_for_mfc(proxy_address)


def loop_mfc_all_online():
    while True:
        thread = Thread(target=mitm_init, daemon=True)
        thread.start()
        thread.join()

        delay_, time_ = script_delay(329.07, 742.89)
        log.query(f"MFC streamers @ {time_}")
        asyncio.run(asyncio.sleep(delay_))


if __name__ == "__main__":
    loop_mfc_all_online()
