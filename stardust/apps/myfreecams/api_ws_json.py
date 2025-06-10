# The generated url expires after 2-3 minutes
import asyncio
import json
import random
import re
import signal
import time
from urllib.parse import unquote

import pandas as pd
from rnet import Message, WebSocket, websocket

import stardust.utils.heliologger as log
from stardust.apps.myfreecams.db_myfreecams import DbMfc
from stardust.apps.myfreecams.handleurls import iNetMfc
from stardust.apps.myfreecams.helper import WS_SERVERS
from stardust.utils.general import script_delay


async def send_message(ws):
    await ws.send(Message.from_text("fcsws_20180422\n"))
    await ws.send(Message.from_text("1 0 0 20071025 0 1/guest:guest\n"))


async def receive_message(ws: WebSocket, server):
    url_params = ""
    arg1 = 0
    count_loop_iterations = 0
    async for socket in ws:
        count_loop_iterations += 1
        chat_data = socket.text.split("%")[0][6:]
        chat_extdata = chat_data[:2]

        # 81 contains the data required to build url for api data
        # which provides all online streamers
        if chat_extdata != "81":
            continue

        clean_text = unquote(socket.text)
        separate_json = re.search("({.+})", clean_text)
        if not separate_json:
            continue

        url_params = json.loads(separate_json.group(0))
        log.debug(url_params)
        # sometimes 81 presents a zero value for arg1
        # In this case, keep checking sockets
        arg1 = url_params["msg"]["arg1"]
        if arg1 > 0:
            log.debug(f"{count_loop_iterations=}")
            break

    if not url_params:
        return

    opts = url_params["opts"]
    key = url_params["respkey"]
    serv = url_params["serv"]
    type_ = url_params["type"]
    arg2 = url_params["msg"]["arg2"]

    api_url = f"https://www.myfreecams.com/php/FcwExtResp.php?host={server}&respkey={key}&type={type_}&opts={opts}&serv={serv}&arg1={arg1}&arg2={arg2}&owner=0&nc=2915592&debug=cams"
    log.debug(api_url)

    return api_url


async def get_socket_api_url():
    """The api url expires relatively quickly"""
    server = random.choice(WS_SERVERS)
    host = f"wss://{server}.myfreecams.com/fcsl"
    api_url = ""
    ws = await websocket(host)

    if ws.ok:
        send_task = asyncio.create_task(send_message(ws))
        receive_task = asyncio.create_task(receive_message(ws, server))

        async def close_ws():
            await ws.close()
            send_task.cancel()
            receive_task.cancel()

        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(close_ws()))

        _, api_url = await asyncio.gather(send_task, receive_task)

    return api_url


def handle_streamers_online(json_):
    db = DbMfc("myfreecams")

    log.info(f"{json_['count']} MFC streamers online")
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


def manage_websocket():
    iNet = iNetMfc()
    while True:
        api_url = asyncio.run(get_socket_api_url())
        json_ = asyncio.run(iNet.get_all_online_streamers(api_url))
        handle_streamers_online(json_)

        delay_, time_ = script_delay(19.07, 42.89)
        log.query(f"MFC streamers @ {time_}")
        time.sleep(delay_)


def loop_mfc_online_streamers():
    loop = asyncio.new_event_loop()
    loop.create_task(manage_websocket())
    loop.run_forever()


if __name__ == "__main__":
    loop_mfc_online_streamers()
