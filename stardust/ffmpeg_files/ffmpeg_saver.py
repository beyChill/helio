import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from subprocess import DEVNULL, PIPE, STDOUT, Popen
from threading import Thread
from time import sleep
from typing import Any

import stardust.utils.heliologger as log
from stardust.apps.chaturbate.handleurls import iNetCb
from stardust.apps.manage_app_db import HelioDB
from stardust.apps.models_app import DataFFmpeg
from stardust.apps.myfreecams.handleurls import iNetMfc
from stardust.apps.myfreecams.helper import chk_online_status, make_playlist
from stardust.config.settings import get_setting
from stardust.ffmpeg_files.ffmpeg_data import FFmpegConfig
from stardust.utils.general import calc_video_size
from stardust.utils.handle_m3u8 import HandleM3u8

config = get_setting()


@dataclass(slots=True)
class CaptureStreamer:
    """
    Start and monitor FFmpeg live stream capture
    """

    data: DataFFmpeg
    db: HelioDB = field(init=False)
    name_: str = field(init=False)
    site: str = field(init=False)
    slug: str = field(init=False)
    process: Popen[str] = field(init=False)
    pid: int = field(default=0, init=False)
    delay_: int = field(init=False)
    max_time: bool = field(default=False, init=False)
    restart_url: Any = field(init=False)

    def __post_init__(self):
        self.site = self.data.site
        self.name_ = self.data.name_
        self.slug = self.data.slug.upper()
        self.db = HelioDB()
        self.delay_ = 12
        self.activate()

    def _std_out(self):
        if config.FFMPEG_DEGUB:
            return open(f"{self.data.file_.parent}/stdout.log", "w+", encoding="utf-8")
        return PIPE

    def set_delay(self, seconds: int):
        self.delay_ = seconds

    def _terminate(self):
        self.process.wait()
        self.process.terminate()

    def subprocess_poll_end(self):
        log.stopped(f"{self.name_} [{self.slug}]")

    def video_duration_end(self):
        log.maxtime(f"{self.name_} [{self.slug}]")

    def activate(self):
        if self.db.query_process_id(self.name_, self.slug):
            log.warning(f"Already capturing {self.name_} {self.slug}")
            return None

        self.process = Popen(
            self.data.args,
            stdin=DEVNULL,
            stdout=self._std_out(),
            stderr=STDOUT,
            start_new_session=True,
            encoding="utf8",
            universal_newlines=True,
        )

        self.pid = self.process.pid

        if self.process.poll() is not None:
            log.warning(f"Unable to capture {self.name_}")
            self.db.write_rm_process_id(self.process.pid)
            return

        today_ = datetime.now().replace(microsecond=0)
        self.db.write_process_id((self.pid, today_, self.name_, self.slug))

        thread = Thread(target=self.subprocess_status, daemon=True)
        thread.start()

    def subprocess_status(self):
        log.capturing(f"{self.name_} [{self.slug}]")
        while True:
            if self.process.poll() is not None:
                self._terminate()
                self.set_delay(9)
                self.subprocess_poll_end()
                break

            if self.check_video_duration():
                self._terminate()
                self.set_delay(0)
                self.video_duration_end()
                self.max_time = True
                self.restart_url = self.db.query_url(self.name_, self.slug)
                break

        self.manage_cap_restart()

    def check_video_duration(self):
        time_value = 0

        if self.process.stdout is None:
            return False

        output = self.process.stdout.readline()

        if "out_time_ms" in (line := output.strip()):
            _, seconds_ = line.split("=")
            time_value = int(seconds_) / 1e6

        if time_value >= config.VIDEO_LENGTH_SECONDS:
            return True

        return False

    def manage_cap_restart(self):
        if not self.data.file_.is_file():
            return None

        calc_video_size(self.name_, self.data.file_, self.slug)

        cap_status, block = self.db.query_cap_status(self.name_)

        if not cap_status or block:
            self.db.write_rm_process_id(self.pid)
            return None

        if not self.max_time:
            sleep(self.delay_)
            self.restart_url = get_restart_url(self.name_, self.slug)

        if self.restart_url is None:
            self.db.write_rm_process_id(self.pid)
            return None

        data = FFmpegConfig(self.name_, self.slug, self.restart_url).return_data

        self.db.write_rm_process_id(self.pid)
        CaptureStreamer(data)


def get_restart_url(name_, slug):
    if slug == "CB":
        results = asyncio.run(iNetCb().get_ajax_url([name_]))

        if not results[0]["url"]:
            if results[0]["room_status"] == "offline":
                log.offline(f"{name_} [{slug}]")
                return None

            log.stopped(f"{name_} [{slug}] is {results[0]['room_status']}")
            return None

        url = results[0]["url"]
        if (data := asyncio.run(HandleM3u8(url).cb_m3u8())) is None:
            return None

        url, *_ = data
        return url

    if slug == "MFC":
        if (data := asyncio.run(iNetMfc().get_all_status([name_]))) is None:
            log.warning(f"The query for {name_} {slug} failed")
            return None

        if not (streamer := chk_online_status(data[0], name_, slug)):
            return None

        session = streamer.result.user.sessions[-1]
        streamer_id = streamer.result.user.id

        playlist_url = make_playlist(session, streamer_id)

        if (url_m3u8 := asyncio.run(HandleM3u8(playlist_url).mfc_m3u8())) is None:
            return None

        HelioDB().write_capture_url((url_m3u8, name_, slug))

        return url_m3u8
