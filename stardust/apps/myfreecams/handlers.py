import json

import pandas as pd
from mitmproxy.http import HTTPFlow

from stardust.apps.myfreecams.db_myfreemcams import DbMfc
from stardust.utils.applogging import HelioLogger

log = HelioLogger()


def handle_streamers_online(flow: HTTPFlow):
    db = DbMfc("myfreecams")
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
    url_data: list = df_url.values.tolist()

    # Again just keeping valued data from the 63 the api provides
    other_data = df.loc[0:, [0, 11, 16, 17, 18, 19, 20, 21, 22]]

    # the dataframe to sql function (tosql) overwrites column heads in table.
    # converting it to a list eliminates issue.
    streamer_data: list = other_data.values.tolist()

    db.write_streamer_data(streamer_data)
    db.write_url_data(url_data)

    return None
