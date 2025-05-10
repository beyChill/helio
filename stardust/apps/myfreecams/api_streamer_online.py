import asyncio

from stardust.apps.manage_app_db import HelioDB
from stardust.apps.manage_capture import start_capture
from stardust.apps.myfreecams.handleurls import MfcNetActions
from stardust.apps.myfreecams.helper import parse_profile
from stardust.apps.myfreecams.models_mfc import MfcModelEx
from stardust.utils.applogging import HelioLogger
from stardust.utils.handle_m3u8 import HandleM3u8

db = HelioDB("myfreecams")
log = HelioLogger()
iNet = MfcNetActions()


async def get_streamers():
    json: MfcModelEx = await iNet.get_all_models()

    site_streamers = [streamer.username for streamer in json.result.data]

    return site_streamers


def compare_streamers(site_streamers: list[str]):
    if not (streamers_in_db := db.query_main_streamers()):
        log.warning("Database contains zero streamers for capture")
        return []

    # Compair db and site streamers lists to determine
    # streamers for capture
    db_streamers_online = [
        (name_, seek_capture)
        for name_, seek_capture in streamers_in_db
        if name_ in site_streamers
    ]

    if not db_streamers_online:
        log.warning("Zero MFC streamers are online")
        return []

    # Next two list comprehensions seperate streamers
    # for db update only and continued actions.
    capture_streamers: list[str] = [
        name_ for name_, seek_capture in db_streamers_online if seek_capture
    ]

    last_broadcast = [(name_,) for name_, _ in db_streamers_online]

    db.write_last_broadcast(last_broadcast)

    count_last_broadcast = len(last_broadcast)
    log.info(f"{len(last_broadcast)} MFC streamers are online")

    if count_last_broadcast > 0:
        log.info(f"Preparing to capture {len(capture_streamers)} MFC streamers")

    return capture_streamers


def capture_process():
    site_streamers = asyncio.run(get_streamers())
    if not (capture_streamers := compare_streamers(site_streamers)):
        log.warning("Zero MFC streamers await capture")
        return

    json_ = asyncio.run(iNet.get_user_profile(capture_streamers))

    parsed_profiles = [parse_profile(json, fetch="all") for json in json_]

    urls = [(url, name_) for url, name_ in parsed_profiles if url]

    new_m3u8 = [
        (HandleM3u8(url).mfc_m3u8(), name_) for url, name_ in urls if url is not None
    ]

    for m3u8, name_ in new_m3u8:
        db.write_capture_url((m3u8, name_))
        log.info(f"{name_}, {m3u8}")
        start_capture([(name_, "mfc", str(m3u8))])


if __name__ == "__main__":
    capture_process()
