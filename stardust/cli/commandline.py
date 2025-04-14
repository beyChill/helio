
import sys
from cmd2 import Cmd
from stardust.apps import __apps__ as apps_module
from stardust.apps.chaturbate.argpar import get_parser

APP_MAPPINGS = {}
for attr in dir(apps_module):
    if attr.startswith("_") and not attr.startswith("__"):
        app_data = getattr(apps_module, attr)
        APP_MAPPINGS[app_data[0]] = app_data[1]

REVERSE_APP_MAPPINGS = {v: k for k, v in APP_MAPPINGS.items()}

print(APP_MAPPINGS)

class CLI(Cmd):
    file = None
    intro = "Type help or ? for command infomation.\n"
    user_prompt = "$"
    prompt = f"{user_prompt}-> "

    cb_get = get_parser()

# def settings_ns_provider(self) -> Namespace:
#     """Populate an argparse Namespace with current settings"""
#     ns = Namespace()
#     ns.app_settings = self.settings
#     return ns


    # @with_argparser(cb_get)
    # def do_get(self,args):
    #     print('capture',args.capture)

    #     if args.capture:
    #         self.poutput(f"capture:{args.streamer}")
    #         return None

    #     if args.data:
    #         self.poutput(f"{args.data}, run query")
    #         return None

    #     print("************")

    #     self.poutput(args)

    #     return None
    

    # def do_get(self, args) -> None:

    #     if not all(data := CliValidations().check_input(line, self.user_prompt)):
    #         return None

    #     # remove possiblity for None
    #     streamer_name = str(data.name_)
    #     streamer: HlsQueryResults = self.get_url(streamer_name)

    #     db_add_streamer(streamer.name_, streamer.domain)

    #     if not all(streamer):
    #         # log.info(f"{streamer.name_} is {streamer.room_status}")
    #         return None

    #     # if recent_api_call():
    #     #     log.info(colored("Awaiting api rest cmd get", "yellow"))
    #     #     sleep(60)
    #     #     log.debug("resuming api call")

    #     if not None in (db_get_pid(streamer.name_)):
    #         log.info(
    #             f"Already capturing {colored(streamer.name_,"yellow")} ({data.site})"
    #         )
    #         return None

    #     if not all(streamer_data := CreateStreamer(*streamer).return_data):
    #         print(streamer_data)
    #         return None

    #     CaptureStreamer(streamer_data)

    #     return None

if __name__=="__main__":
    c=CLI()
    sys.exit(c.cmdloop())