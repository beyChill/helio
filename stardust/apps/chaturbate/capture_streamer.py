import asyncio

# from collections.abe import Iterable - give pylint error
from typing import Iterable
from dataclasses import dataclass, field
from io import TextIOWrapper
from logging import getLogger
from pathlib import Path
from random import choice
from subprocess import DEVNULL, PIPE, STDOUT, Popen
from threading import Thread
from time import sleep, strftime


# from termcolor import colored

# from app.database.db_query import db_cap_status, db_get_saved_url
# from app.database.db_writes import db_remove_pid, db_site_domain, db_update_pid

# # from app.log.logger import FFLOG, CustomLogger
# from app.https.clients import check_online_status
# from app.sites.create_streamer import CreateStreamer
# from app.sites.getstreamerurl import get_streamer_url

# # from app.utils.general_utils import recent_api_call
# from app.utils.named_tuples import HlsQueryResults, StreamerData, StreamerWithPid

# log = getLogger(__name__)


@dataclass(
    slots=True,
    init=False,
    frozen=True,
    repr=False,
    eq=False,
)
class CaptureError(Exception):
    msg: str

    def __init__(self, msg) -> None:
        object.__setattr__(self, "msg", msg)


@dataclass(slots=True)
class CaptureStreamer:
    data: StreamerData
    site_slug: str = field(init=False, default="[CB]")
    file: Path = field(init=False)
    process: Popen[bytes] = field(init=False)
    pid: int = field(default=0, init=False)
    args_ffmpeg: list = field(default_factory=list)
    capture_time: int = field(default=1800, init=False)
    sleep_time: int = field(default=90, init=False)

    def __post_init__(self):
        self.create_path()
        self.file = Path(self.data.path_, self.data.file).joinpath()
        self.args_ffmpeg = self.ffmpeg_args()
        if self.data.url:
            self.activate()

    def set_sleep_time(self, time_: int):
        self.sleep_time = time_

    def create_path(self):
        self.data.path_.mkdir(parents=True, exist_ok=True)

    def generate_url(self, name_: str, domain: str):
        url = db_get_saved_url(name_)
        db_site_domain(name_, None)
        url_query: list[HlsQueryResults] = asyncio.run(get_streamer_url([name_]))
        new_url = url_query[0].url
        db_site_domain(name_, new_url)
        # characters = "abcdefghijklmnopqrstuvwxyz0123456789"
        # random_string = "".join(choice(characters) for _ in range(64))
        # url = f"https://{domain}/live-hls/amlst:{name_}-sd-{random_string}_trns_h264/playlist.m3u8"
        # print(url)
        return url

    def ffmpeg_args(self):
        args = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-progress",
            "pipe:1",
            "-i",
            self.data.url,
            *self.data.metadata,
            "-t",
            f"{self.capture_time}",
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            self.file,
        ]
        return args

    def std_out(self):
        ffmpeg_debug = False
        if ffmpeg_debug:
            return open(f"{self.data.path_}/stdout.log", "w+", encoding="utf-8")

        return PIPE

    def time_limit_reached(self, process: Popen):
        time_value = 0

        if process.stdout is None:
            return False

        if process.poll is None:
            return False

        output = process.stdout.readline()
        if "out_time_ms" in (line := output.strip()):
            _, seconds_ = line.split("=")
            time_value = int(seconds_) / 1e6

        if time_value >= self.capture_time:
            return True

        return False

    # def handle_rate_limit(self):
    #     rate_limit_concern = recent_api_call()

    #     if rate_limit_concern:
    #         log.info(
    #             f"{strftime("%H:%M:%S")}: {colored('Pausing api action for rate limit risk','yellow')}"
    #         )
    #         self.set_sleep_time(90)

    #         return True
    #     return False

    def get_available_url(self, name_: str, hls_query: list[HlsQueryResults]):
        code = asyncio.run(check_online_status([[name_]]))

        if code == 200:
            return hls_query

        sleep(self.sleep_time)
        hls_query = asyncio.run(get_streamer_url([name_]))

        return hls_query

    def get_restart_url(self, data: tuple[bool, str, str]):
        max_time, name_, domain = data

        hls_query = [
            HlsQueryResults(
                name_,
                success=True,
                room_status="public",
                url=self.generate_url(name_, domain),
                domain=domain,
            )
        ]

        if not max_time:
            sleep(self.sleep_time)
            hls_query = self.get_available_url(name_, hls_query)

        return hls_query

    def poll_end(self):
        log.debug(
            f"{strftime('%H:%M:%S')}: {colored(f'{self.data.name_} {self.site_slug} stopped', 'yellow')}"
        )

    def duration_end(self):
        log.info(
            f"{strftime('%H:%M:%S')}: {colored(f'{self.data.name_} {self.site_slug} reached time duration', 'yellow')}"
        )

    def subprocess_status(self, process: Popen):
        max_time: bool = False

        try:
            log.info(
                strftime("%H:%M:%S")
                + f": Capturing {colored(self.data.name_, 'green')}"
            )
            while True:
                if process.poll() is not None:
                    self.set_sleep_time(9)
                    self.poll_end()
                    break

                duration_reached = self.time_limit_reached(process)
                if duration_reached:
                    self.set_sleep_time(0)
                    self.duration_end()
                    max_time = True
                    break

            # if self.handle_rate_limit():
            #     sleep(self.sleep_time)
            #     log.info(
            #         f"{strftime("%H:%M:%S")}: {colored('resuming api actions','yellow')}"
            #     )

            follow, block, domain = db_cap_status(self.data.name_)

            db_remove_pid(self.pid)

            if not bool(follow) or bool(block):
                return None

            url_data = (max_time, self.data.name_, domain)
            data = self.get_restart_url(url_data)

            re_streamer = [
                CreateStreamer(*x).return_data for x in data if isinstance(x, Iterable)
            ]

            _ = [CaptureStreamer(x) for x in re_streamer if isinstance(x, Iterable)]
        except CaptureError as e:
            log.info(e.msg)

    def activate(self):
        process = Popen(
            self.args_ffmpeg,
            stdin=DEVNULL,
            stdout=self.std_out(),
            stderr=STDOUT,
            start_new_session=True,
            encoding="utf8",
            universal_newlines=True,
        )

        if process.poll() is not None:
            return None

        self.pid = process.pid

        streamer_subprocess = StreamerWithPid(self.pid, self.data.name_, self.data.site)

        db_update_pid(streamer_subprocess)

        thread = Thread(target=self.subprocess_status, args=(process,), daemon=True)
        thread.start()
        del self
