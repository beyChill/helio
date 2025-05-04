import asyncio
from stardust.apps.myfreecams.handleurls import MfcNetActions
from stardust.utils.applogging import HelioLogger

log = HelioLogger()

#Hitting rate limit at 37 api calls
def request_profiles(names: list[str]):
    iNet = MfcNetActions()
    profiles = asyncio.run(iNet.get_user_profile(names))
    for profile in profiles:
        name_ = profile.method.split("/")[-1]

        if profile.result.message != "user found":
            log.warning(
                f"{name_} does not match a MFC streamer. Perhaps check spelling or capitalizaton",
            )
            continue

        if not profile.result.user:
            continue

        if not profile.result.user.sessions:
            log.warning(f"{name_} is offline")
            continue

        if profile.result.user.sessions:
            log.info(f"User session: {name_}, server name: {profile.result.user.sessions[0].server_name}")