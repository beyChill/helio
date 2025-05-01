import asyncio
from stardust.apps.myfreecams.handleurls import MfcNetActions
from stardust.utils.applogging import HelioLogger, loglvl

log = HelioLogger()

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
    ("carolain39", 43476424),
    ("Shayblonde", 45288572),
    ("MaiaMini", 46279687),
    ("AmyCarrera", 42524339),
    ("MissKennya", 36342394),
    ("MaraMaxine", 44420365),
    ("kewcumber", 34429637),
    ("Crazyladya", 46197359),
    ("SabrinaKali", 45681864),
    ("JulietBabe", 46078604),
    ("DarkElf_", 40229828),
    ("Bonny_Moan", 45363934),
    ("SophiaNicolle", 44888348),
    ("warmhoney888", 42104205),
    ("NADINNNE", 23514778),
    ("LovableMilf", 31331423),
    ("SiennaSunset", 45352510),
    ("AlenaBays", 45091901),
    ("Sweetmayaxx", 44925191),
    ("EvelinaFox", 34605531),
    ("MirabelaSweet", 17331898),
    ("Foxy_red333", 29816794),
    ("petitebabixo", 44986762),
    ("Juliageuss", 42958810),
    ("CassidyJoy", 20092937),
    ("Hot_and_Sweet", 25951066),
    ("MagiccEyesss", 41073171),
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
        print(profile.status, profile.name_)
    return profiles


ty = request_app_profile(data)
log.app(loglvl.SUCCESS, f"{len(ty)} of {len(data)} completed")
# EvaEvelin
