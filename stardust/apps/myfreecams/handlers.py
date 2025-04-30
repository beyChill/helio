import json

import pandas as pd
from mitmproxy.http import HTTPFlow
from stardust.apps.myfreecams.db_write import streamers_online, streamers_url_data
from stardust.utils.applogging import HelioLogger, loglvl

log = HelioLogger()

def handle_streamers_online(flow: HTTPFlow):
    if flow.response is None:
        return

    if (body := flow.response.text) is None:
        return

    # json.loads(body)["rdata"]
    # might fail to receive or process data
    # happened once randomly. Bug could the result
    # of a different problem elsewhere. Keep watching
    data = json.loads(body)["rdata"]
    df = pd.DataFrame((data[1:]))

    # Not sure of simple method to include all data from api (63 columns)
    # keeping most valuable colums vs all columns
    df_url = df.iloc[:, :8]
    url_data = df_url.values.tolist()

    # Again just keeping valued data from the 63 the api provides
    other_data = df.loc[0:, [0, 11, 16, 17, 18, 19, 20, 21, 22]]
    # the dataframe to sql function (tosql) overwrites column heads in table.
    # converting it to a list eliminates issue.
    values = other_data.values.tolist()

    log.app(loglvl.SUCCESS,f"Evaluated {len(values)} MFC streamers")
    streamers_online(values, url_data)
