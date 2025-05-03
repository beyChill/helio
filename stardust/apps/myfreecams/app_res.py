from mitmproxy import http

from stardust.apps.myfreecams.handlers import handle_streamers_online
from stardust.utils.applogging import HelioLogger


log = HelioLogger()


class AppResponse:
    def response(self, flow: http.HTTPFlow) -> None:
        url = flow.request.pretty_url

        if url.__contains__("playlist"):
            log.info(f"response: {url}")

        if url.endswith("debug=cams"):
            handle_streamers_online(flow)
            return
