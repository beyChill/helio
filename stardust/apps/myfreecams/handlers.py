import json

import pandas as pd
from mitmproxy.http import HTTPFlow
from stardust.apps.myfreecams.db_write import streamers_online, streamers_url_data


def handle_streamers_online(flow: HTTPFlow):
    if flow.response is None:
        return

    if (body := flow.response.text) is None:
        return

    # might fails to receive or process data
    data = json.loads(body)["rdata"]
    df = pd.DataFrame((data[1:]))
    df_url = df.iloc[:, :8]
    url_data = df_url.values.tolist()

    # Not sure of simplier method to include all data from api
    # droping most of columns with high null rates.

    other_data = df.loc[0:, [0, 11, 16, 17, 18, 19, 20, 21, 22]]
    # the dataframe to sql keeps overwrting column heads.
    # converting it to a list eliminates issue.
    values = other_data.values.tolist()

    streamers_online(values, url_data)
