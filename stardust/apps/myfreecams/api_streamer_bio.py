import asyncio
from stardust.apps.myfreecams.handleurls import MfcNetActions


data = [
    ("ArtemisArte", 45858003),
    ("MikaSoul", 45616495),
    ("TiffanyTrue", 45919543),
    ("groovynights", 29696009),
    ("Lpell1", 45443843),
    ("DeoMatissta", 22619828),
    ("ScarletchaseX", 46245165),
    ("Goldieee", 35597980),
    ("PennyDolce", 44402338),
    ("RachelRave", 45585861),
]


iNet = MfcNetActions()


def request_profiles(names: list[str]):
    profiles = asyncio.run(iNet.get_user_profile(names))
    for profile in profiles:
        name_ = profile.method.split("/")[-1]

        if profile.result.message != "user found":
            print(
                name_,
                "Name did not match a MFC streamer. Perhaps check spelling or capitalizaton",
            )
            continue
        if not profile.result.user:
            continue
        if not profile.result.user.sessions:
            print(
                name_,
                "user is offline",
            )
        if profile.result.user.sessions:
            print(name_, profile.result.user.sessions[0].server_name)


def request_app_profile(data: list[tuple[str, int]]):
    profiles = asyncio.run(iNet.get_streamer_app_profile(data))
    for profile in profiles:
        print(profile.name_, profile.status)


request_app_profile(data)
# EvaEvelin
