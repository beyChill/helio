import argparse
import asyncio
import sys

from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser, with_category

from stardust.apps.chaturbate.cli import Chaturbate
from stardust.apps.stripchat.cli import StripChat
from stardust.config.chroma import rgb
from stardust.utils.applogging import HelioLogger
from stardust.utils.general import check_helio_github_version, get_app_name
from stardust.utils.handlesignal import SignalManager

log = HelioLogger()


def run_async_in_thread(coro):
    """Run asynchronous tasks in separate threads"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.close()


class HelioCli(Cmd):
    """
    AppGroup dynamically runs the app's cli.
    """

    app_prompt = ""
    prompt = rgb("Helio--> ", "green")

    def __init__(self, *args, **kwargs):
        # gotta have this or neither the plugin or cmd2 will initialize
        super().__init__(*args, auto_load_commands=False, **kwargs)

        self._chaturbate = Chaturbate()
        self._stripchat = StripChat()

    load_parser = Cmd2ArgumentParser()
    load_parser.add_argument("app", choices=["cb", "sc"])

    def _new_prompt(self, prompt_):
        self.prompt = rgb(f"{prompt_}--> ", "green")

    @with_category("Helio Commands")
    @with_argparser(load_parser)
    def do_app(self, ns: argparse.Namespace):
        """Access the cli for a given site"""
        slug, name_ = get_app_name(ns.app)

        self.app_prompt = slug
        if name_ == "chaturbate":
            self.register_command_set(self._chaturbate)

        if name_ == "stripchat":
            self.register_command_set(self._stripchat)

        try:
            app_slug = slug.upper()
            self.poutput(f"{name_} active")
            self._new_prompt(app_slug)

        except Exception as e:
            log.error(e)
            self.poutput(f"{name_} already loaded")

    @with_category("Helio Commands")
    @with_argparser(load_parser)
    def do_unapp(self, ns: argparse.Namespace):
        slug, name_ = get_app_name(ns.app)
        if not name_:
            return None

        if ns.app == slug:
            self.unregister_command_set(self._chaturbate)

        if ns.app == slug:
            self.unregister_command_set(self._stripchat)

        if ns.app != self.app_prompt:
            print(ns.app)
            return None

        self.poutput("Helio active")
        self.prompt = rgb("Helio--> ", "green")

    def do_version(self, _) -> None:
        asyncio.run(check_helio_github_version())


def app_cli_main(**kwargs):
    SignalManager().register_signals()
    sys.exit(HelioCli().cmdloop())


if __name__ == "__main__":
    app_cli_main()
