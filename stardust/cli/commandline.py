import asyncio
import sys
from argparse import Namespace
from cmd2 import (
    Cmd,
    Cmd2ArgumentParser,
    categorize,
    with_argparser,
)

from stardust.apps.arg_parser import cap_status, set_logs
from stardust.apps.camsoda.cli import CamSoda
from stardust.apps.chaturbate.cli import Chaturbate
from stardust.apps.myfreecams.cli import MyFreeCams
from stardust.apps.shared_cmds import cmd_cap, cmd_off, cmd_stop_all_captures
from stardust.apps.stripchat.cli import StripChat
from stardust.config.chroma import rgb
import stardust.utils.heliologger as log
from stardust.utils.general import (
    check_helio_github_version,
    get_app_name,
    get_app_slugs,
)
from stardust.utils.heliologger import set_permission


def run_async_in_thread(coro):
    """Run asynchronous tasks in separate threads"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.close()


class HelioCli(Cmd):
    """
    Manage cli to interact with several sites.
    """

    intro = log.info("Type help or ? for command infomation")
    app_prompt = ""
    slug = ""
    name_ = ""
    instance_ = ""
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
        self.camsoda = CamSoda()
        self.chaturbate = Chaturbate()
        self.myfreecams = MyFreeCams()
        self.stripchat = StripChat()

    load_parser = Cmd2ArgumentParser()
    load_parser.add_argument("app", choices=get_app_slugs())

    def _new_prompt(self):
        if self.slug is not None:
            self.prompt = rgb(f"{self.slug.upper()}--> ", self.color)

        if self.slug is None:
            self.prompt = rgb("Helio--> ", "green")

    @with_argparser(load_parser)
    def do_load(self, ns: Namespace):
        """Activate the cli for a given site"""

        # automating do_unload
        if self.instance_:
            self.do_unload(self.slug)

        if not self._get_cli_prompt(ns.app):
            return

        self.app_prompt = self.slug

        self.instance_ = getattr(self, self.name_)

        if ns.app == self.slug.lower():
            self.register_command_set(self.instance_)

        try:
            self.poutput(f"{self.name_} cli is ready")
            self._new_prompt()

        except Exception as e:
            log.error(e)
            self.poutput(f"{self.name_} already loaded")

    @with_argparser(load_parser)
    def do_unload(self, ns: Namespace):
        """Make the app cli inactive, threaded functions using asyncio.run_forever() will continue to run"""
        if not self._get_cli_prompt(ns.app):
            return

        self.instance_ = getattr(self, self.name_)

        if ns.app == self.slug.lower():
            self.unregister_command_set(self.instance_)

        if ns.app != self.app_prompt:
            return None

        self.poutput("Helio active")
        self.prompt = rgb("Helio--> ", "green")

    @with_argparser(set_logs())
    def do_log(self, arg: Namespace):
        level = arg.level.lower()
        value = ""

        if arg.value == "on":
            value = arg.level.upper()

        if arg.value == "off":
            value = None

        set_permission(level, value)

    def do_quit(self, arg):
        """Quit Helio gracefully."""
        cmd_stop_all_captures()
        self.poutput("Shutting down apps")
        return True

    def do_version(self, _) -> None:
        """Compare app version with GitHub version"""
        asyncio.run(check_helio_github_version())

    def _get_cli_prompt(self, app: str):
        data = get_app_name(app)
        if not data:
            return False

        slug, name_, color = data
        self.slug = slug
        self.name_ = name_
        self.color = color
        return True

    @with_argparser(cap_status())
    def do_cap(self, arg: Namespace) -> None:
        cmd_cap(arg.sort)

    @with_argparser(cap_status())
    def do_off(self, arg: Namespace) -> None:
        cmd_off(arg.sort)

    categorize(
        (do_load, do_unload, do_log, do_version, do_quit, do_version, do_cap, do_off),
        "Helio commands",
    )


def app_cli_main(**kwargs):
    sys.exit(HelioCli().cmdloop())


if __name__ == "__main__":
    app_cli_main()
