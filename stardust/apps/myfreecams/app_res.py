from mitmproxy import http

from stardust.apps.myfreecams.handlers import handle_streamers_online
from stardust.config.settings import get_db_setting
from stardust.utils.applogging import HelioLogger

MFC_DB_FOLDER = get_db_setting().MFC_DB_FOLDER
log = HelioLogger()


class AppResponse:
    def response(self, flow: http.HTTPFlow) -> None:
        url = flow.request.pretty_url

        if url.__contains__("playlist"):
            print("response", url)

        if url.endswith("debug=cams"):
            handle_streamers_online(flow)
            return
