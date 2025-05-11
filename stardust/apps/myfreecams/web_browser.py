import asyncio
from random import choice
from seleniumbase import SB


def launch_sb_for_mfc(proxy):
    """
    Launch seleniumbase on myfreecams.com
    MyFreeCams api sends a list of... users
    The api generates random string. Haven't figured
    a method to replicate the api generated links.
    
    """
    # add these args to view the brower
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
        proxy=proxy,
        headed=headed,
        headless2=headless2,
        window_size=(f"{window_size}"),
        window_position=window_position,
    ) as sb:
        url = "https://www.myfreecams.com"
        sb.activate_cdp_mode(url)

        # delay for myfreecams api to respond,api seems a bit slow
        # refactor to probably recieve a site trigger.
        asyncio.run(asyncio.sleep(2))
