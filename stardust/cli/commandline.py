import argparse
import asyncio
import sys

from cmd2 import (
    Cmd,
    Cmd2ArgumentParser,
    argparse_custom,
    categorize,
    with_argparser,
    with_category,
)

from stardust.apps.camsoda.cli import CamSoda
from stardust.apps.chaturbate.cli import Chaturbate
from stardust.apps.myfreecams.cli import MyFreeCams
from stardust.apps.stripchat.cli import StripChat
from stardust.config.chroma import rgb
from stardust.utils.applogging import HelioLogger
from stardust.utils.general import check_helio_github_version, get_app_name, get_app_slugs

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
    intro = log.info("Type help or ? for command infomation.\n")
    app_prompt = ""
    slug = ""
    name_ = ""
    prompt = rgb("Helio--> ", "green")

    def __init__(self, *args, **kwargs):
        # gotta have this or neither the plugin or cmd2 will initialize
        super().__init__(*args, auto_load_commands=False, **kwargs)
        del Cmd.do_macro
        del Cmd.do_run_pyscript
        del Cmd.do_shortcuts
        del Cmd.do_shell
        del Cmd.do_alias
        del Cmd.do_edit
        del Cmd.do_run_script
        self._camsoda = CamSoda()
        self._chaturbate = Chaturbate()
        self._myfreecams = MyFreeCams()
        self._stripchat = StripChat()

    load_parser = Cmd2ArgumentParser()
    load_parser.add_argument("app", choices=get_app_slugs())

    def _new_prompt(self):
        if self.slug is not None:
            self.prompt = rgb(f"{self.slug.upper()}--> ", self.color)

        if self.slug is None:
            self.prompt = rgb("Helio--> ", "green")

    @with_category("Helio Commands")
    @with_argparser(load_parser)
    def do_app(self, ns: argparse.Namespace):
        """Access the cli for a given site"""
        if not self._get_app_info(ns.app):
            return

        self.app_prompt = self.slug

        mod_name = f"_{self.name_}"
        instance_ = getattr(self, mod_name)

        if ns.app == self.slug.lower():
            self.register_command_set(instance_)

        try:
            self.poutput(f"{self.name_} interactions are ready")
            self._new_prompt()

        except Exception as e:
            log.error(e)
            self.poutput(f"{self.name_} already loaded")

    @with_category("Helio Commands")
    @with_argparser(load_parser)
    def do_unapp(self, ns: argparse.Namespace):
        """Unload app from memory, threaded functions will continue to run"""
        if not self._get_app_info(ns.app):
            return

        mod_name = f"_{self.name_}"
        instance_ = getattr(self, mod_name)

        if ns.app == self.slug.lower():
            self.unregister_command_set(instance_)

        if ns.app != self.app_prompt:
            return None

        self.poutput("Helio active")
        self.prompt = rgb("Helio--> ", "green")

    def do_version(self, _) -> None:
        """Check currency of app with GitHub release"""
        asyncio.run(check_helio_github_version())

    def _get_app_info(self, app: str):
        data = get_app_name(app)
        if not data:
            return None

        slug, name_, color = data
        self.slug = slug
        self.name_ = name_
        self.color = color
        return True

    def do_quit(self, arg):
        """Quit Helio gracefully."""
        self.poutput("Shutting down apps")
        return True

    categorize((do_app, do_unapp, do_version, do_quit), "Helio commands")


def app_cli_main(**kwargs):
    sys.exit(HelioCli().cmdloop())


if __name__ == "__main__":
    app_cli_main()
