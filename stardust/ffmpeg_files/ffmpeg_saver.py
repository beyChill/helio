import asyncio
import os
from dataclasses import dataclass, field
from subprocess import DEVNULL, PIPE, STDOUT, Popen
from threading import Thread
from time import sleep
from typing import Any

from stardust.apps.chaturbate.handleurls import NetActions
from stardust.apps.manage_app_db import HelioDB
from stardust.apps.myfreecams.handleurls import MfcNetActions
from stardust.apps.myfreecams.helper import parse_profile
from stardust.config.constants import DataFFmpeg
from stardust.config.settings import get_setting
from stardust.ffmpeg_files.ffmpeg_data import FFmpegConfig
from stardust.utils.applogging import HelioLogger, loglvl
from stardust.utils.general import calc_size
from stardust.utils.handle_m3u8 import HandleM3u8

# process_cb_hls
log = HelioLogger()
config = get_setting()


@dataclass(slots=True)
class CaptureStreamer:
    """
    Start and monitor FFmpeg live stream capture
    """

    data: DataFFmpeg
    db: HelioDB = field(init=False)
    site: str = field(init=False)
    process: Popen[str] = field(init=False)
    pid: int = field(default=0, init=False)
    delay_: int = field(init=False)
    max_time: bool = field(default=False, init=False)
    restart_url: Any = field(init=False)

    def __post_init__(self):
        self.site = self.data.site
        self.db = HelioDB(self.site)
        self.delay_=12
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
        log.app(loglvl.STOPPED, f"{self.data.name_} [{self.data.slug}]")

    def video_duration_end(self):
        log.app(loglvl.MAXTIME, f"{self.data.name_} [{self.data.slug}]")

    def activate(self):
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
        self.db.write_process_id((self.pid, self.data.name_))

        thread = Thread(target=self.status_subprocess, daemon=True)
        thread.start()

    def status_subprocess(self):
        log.app(loglvl.CAPTURING, f"{self.data.name_} [MFC]")
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
                self.restart_url = self.db.query_url(self.data.name_)
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
        cap_status = self.db.query_cap_status(self.data.name_)

        if not cap_status:
            self.db.write_rm_process_id(self.pid)
            return None

        seek_capture, block = cap_status

        if seek_capture is None or block is not None:
            self.db.write_rm_process_id(self.pid)
            return None

        if not self.max_time:
            self.restart_url = self.get_restart_url()

        if not self.restart_url:
            self.db.write_rm_process_id(self.pid)
            return None

        asyncio.run(write_video_size(self.data.name_, self.data.file_, self.site))

        data = FFmpegConfig(self.data.name_, self.data.slug, self.restart_url).return_data
        
        CaptureStreamer(data)


    def get_restart_url(self):
        sleep(self.delay_)
        url = get_url(self.data.name_, self.site)
        return url


def get_url(name_, site):

    if site == "chaturbate":
        results = asyncio.run(NetActions().get_ajax_url([name_]))

        if not results[0]["url"]:
            log.app(loglvl.STOPPED, f"{name_} [{site}] {results[0]['room_status']}")
            return None

        url = results[0]["url"]
        return HandleM3u8(url).new_cb_m3u8()

    if site == "myfreecams":
        json_ = asyncio.run(MfcNetActions().get_user_profile([name_]))
        url_ = parse_profile(json_[0])
        return url_


async def write_video_size(name_, file, site):
    raw_size = os.stat(file).st_size
    file_size = calc_size([raw_size])
    values = (file_size, name_)
    HelioDB(site).write_video_size(values)
