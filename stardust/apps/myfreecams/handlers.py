import json

import pandas as pd
from mitmproxy.http import HTTPFlow
from stardust.apps.myfreecams.db_write import streamers_online


def handle_streamers_online(flow:HTTPFlow):
    if flow.response is None:
        return

    if (body := flow.response.text) is None:
        return

    # might fails to receive or process data
    data = json.loads(body)["rdata"]
    df = pd.DataFrame((data[1:]))

    # Not sure of simplier method to include all data from api
    # droping most of columns with high null rates.
    
    df.drop(columns=df.columns[-38:], axis=1, inplace=True)
    # the dataframe to sql keeps overwrting column heads.
    # converting it to a list eliminates issue.
    values = df.values.tolist()

    streamers_online(values)
