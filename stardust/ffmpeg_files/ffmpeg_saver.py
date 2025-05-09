from dataclasses import dataclass, field
from datetime import datetime
from subprocess import DEVNULL, PIPE, STDOUT, Popen
from threading import Thread
from time import sleep
from typing import Any

from stardust.apps.manage_app_db import HelioDB
from stardust.apps.models_app import DataFFmpeg
from stardust.config.settings import get_setting
from stardust.ffmpeg_files.ffmpeg_data import FFmpegConfig
from stardust.utils.applogging import HelioLogger, loglvl
from stardust.utils.general import calc_video_size, get_url

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
        log.app(loglvl.STOPPED, f"{self.data.name_} [{self.data.slug.upper()}]")

    def video_duration_end(self):
        log.app(loglvl.MAXTIME, f"{self.data.name_} [{self.data.slug.upper()}]")

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

        if self.process.poll() is not None:
            log.warning(f"Unable to capture {self.data.name_}")
            self.db.write_rm_process_id(self.process.pid)
            return

        today_ = datetime.now().replace(microsecond=0)
        self.db.write_process_id((self.pid, today_, self.data.name_))

        thread = Thread(target=self.status_subprocess, daemon=True)
        thread.start()

    def status_subprocess(self):
        log.app(loglvl.CAPTURING, f"{self.data.name_} [{self.data.slug.upper()}]")
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
        if not self.data.file_.is_file():
            return None
        calc_video_size(self.data.name_, self.data.file_, self.site)

        if not (cap_status := self.db.query_cap_status(self.data.name_)):
            self.db.write_rm_process_id(self.pid)
            return None

        seek_capture, block = cap_status

        if not seek_capture or block:
            self.db.write_rm_process_id(self.pid)
            return None

        if not self.max_time:
            sleep(self.delay_)
            self.restart_url = get_url(self.data.name_, self.site)

        if not self.restart_url:
            self.db.write_rm_process_id(self.pid)
            return None

        data = FFmpegConfig(
            self.data.name_, self.data.slug, self.restart_url
        ).return_data

        CaptureStreamer(data)
