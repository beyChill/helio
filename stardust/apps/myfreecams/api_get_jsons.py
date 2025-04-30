import asyncio
from pathlib import Path
from threading import Thread
from mitmproxy import ctx, addons
from mitmproxy.master import Master
from mitmproxy.options import Options

from stardust.apps.myfreecams.app_req import AppRequest
from stardust.apps.myfreecams.app_res import AppResponse
from stardust.apps.myfreecams.browser import launch_sb_for_mfc
from stardust.utils.timer import AppTimerSync


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

    # server needs an instance in time to start
    async def _wait_for_proxyserver(self):
        while not self._has_proxy_address():
            await asyncio.sleep(0.009)

    def _has_proxy_address(self):
        if not (ipaddress := ctx.master.addons.lookup["proxyserver"].listen_addrs()):
            return None

        if len(ipaddress[0]) == 2:
            addr, port = ipaddress[0]
            self.ip_address = f"{addr}:{port}"
            return self.ip_address

        addr, port = ipaddress[1]
        self.ip_address = f"{addr}:{port}"

        # Seleniumbase Chrome doesn't support IPv6 Proxy/
        # Review SeleniumBase's code, GitHub: SeleniumBase / seleniumbase / core / proxy_helper.py
        # Selenium does support IPv6. Leaving code in
        # this function just incase we dump seleniumbase.

        # addr, port, *_ = ipaddress[0]
        # self.ip_address = f"[{addr}]:{port}"

        return self.ip_address

    async def start(self):
        asyncio.run_coroutine_threadsafe(ctx.master.run(), self.loop)
        # asyncio.run(self._wait_for_proxyserver())
        while not self._has_proxy_address():
            await asyncio.sleep(0.009)

    @property
    def proxy_address(self):
        return self.ip_address


@AppTimerSync
def get_mfc_online_json():
    init_ = MitmServer()
    try:
        launch_sb_for_mfc(init_.proxy_address)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    get_mfc_online_json()
