# Primary purpose is to use websockets to obtain
# the data to build api url to acquire json 
# containting all online streamers
# The generated url expires after 2-3 minutes
import asyncio
import json
import random
import re
import time
from urllib.parse import unquote

from rnet import Message, WebSocket, websocket

import stardust.utils.heliologger as log
from stardust.apps.myfreecams.db_myfreecams import DbMfc
from stardust.apps.myfreecams.handleurls import iNetMfc
from stardust.apps.myfreecams.helper import WS_SERVERS
from stardust.utils.general import script_delay


async def send_message(ws):
    await ws.send(Message.from_text("fcsws_20180422\n\0"))
    await ws.send(Message.from_text("1 0 0 20071025 0 1/guest:guest\n\0"))


async def receive_message(ws: WebSocket, server):
    url_params = ""
    count_loop_iterations = 0

    async for socket in ws:
        count_loop_iterations += 1
        target_data = socket.text.split()[0]

        # sockets ending 81 contain the data required to build url for api call
        # This url will provide json of all online streamers
        if target_data not in ["00025481", "00025581", "00025681", "00025781"]:
            continue

        clean_text = unquote(socket.text)

        if not (separate_json := re.search("({.+})", clean_text)):
            continue

        url_params = json.loads(separate_json.group(0))
        log.debug(url_params)
        log.debug(f"{count_loop_iterations=}")
        break

    if not url_params:
        return

    opts = url_params["opts"]
    key = url_params["respkey"]
    serv = url_params["serv"]
    type_ = url_params["type"]
    arg1 = url_params["msg"]["arg1"]
    arg2 = url_params["msg"]["arg2"]

    api_url = f"https://www.myfreecams.com/php/FcwExtResp.php?host={server}&respkey={key}&type={type_}&opts={opts}&serv={serv}&arg1={arg1}&arg2={arg2}&owner=0&nc=2915592&debug=cams"
    log.debug(api_url)

    return api_url


async def get_socket_api_url():
    """Gather data from websockets to generate live url which expires relatively quickly"""
    api_url = ""
    server = random.choice(WS_SERVERS)
    host = f"wss://{server}.myfreecams.com/fcsl"
    ws = await websocket(host)

    async with ws:
        if ws.ok:
            send_task = asyncio.create_task(send_message(ws))
            receive_task = asyncio.create_task(receive_message(ws, server))

            try:
                _, api_url = await asyncio.gather(send_task, receive_task)
            except Exception as e:
                log.error(e)

    return api_url


def handle_streamers_online(json_):
    db = DbMfc("myfreecams")

    log.info(f"{json_['count']} MFC streamers online")
    data = json_["rdata"]

    # populate table with only data used for m3u8 creation
    # json columns headers: ["nm", "sid", "uid", "vs", "pid", "lv", "camserv", "phase"]
    url_data = [x[0:8] for x in data[1:-1]]

    # api returns tons of data Helio doesn't use. Picking and
    # choosing the desired data columns
    # json columns headers: ["nm", "creation" "new_model", "missmfc", "camscore", "continent", "flags", "rank", "rc"]
    # json data: ['ArtemisArte', 1725448438, 0, 0, 78.2, 'EU', 33897504, 0, 4]
    streamer_data = [[x[0], x[11], *x[16:23]] for x in data[1:-1]]

    db.write_streamer_data(streamer_data)
    db.write_url_data(url_data)

    return None


def manage_websocket():
    iNet = iNetMfc()
    while True:
        api_url = asyncio.run(get_socket_api_url())
        json_ = asyncio.run(iNet.get_all_online_streamers(api_url))
        handle_streamers_online(json_)

        delay_, time_ = script_delay(317.47, 421.389)
        log.query(f"MFC streamers @ {time_}")
        time.sleep(delay_)


def loop_mfc_online_streamers():
    loop = asyncio.new_event_loop()
    loop.create_task(manage_websocket())
    loop.run_forever()


if __name__ == "__main__":
    loop_mfc_online_streamers()
