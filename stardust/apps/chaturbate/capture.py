import asyncio
from dataclasses import dataclass, field
from subprocess import DEVNULL, PIPE, STDOUT, Popen
from threading import Thread
from time import sleep

from stardust.apps.chaturbate.db_query import query_cap_status, query_url
from stardust.apps.chaturbate.db_write import write_pid, write_remove_pid
from stardust.apps.chaturbate.handleurls import CbUrls
from stardust.apps.chaturbate.set_streamer_data import FFmpegData
from stardust.config.constants import DataFFmpeg
from stardust.config.settings import get_setting
from stardust.utils.applogging import AppLogger, loglvl
from stardust.utils.general import process_hls

log = AppLogger()
config = get_setting()


@dataclass(slots=True)
class CaptureStreamer(CbUrls):
    """
    Start and monitor FFmpeg live stream capture
    """

    data: DataFFmpeg
    site: str = field(default="chaturbate", init=False)
    process: Popen[str] = field(init=False)
    pid: int = field(default=0, init=False)
    delay_: int = field(default=12, init=False)
    max_time: bool = field(default=False, init=False)

    def __post_init__(self):
        self.activate()

    def _std_out(self):
        if config.FFMPEG_DEGUB:
            return open(f"{self.data.file_.parent}/stdout.log", "w+", encoding="utf-8")
        return PIPE

    @classmethod
    def set_delay(cls, seconds: int):
        cls.delay_ = seconds

    def _terminate(self):
        self.process.wait()
        self.process.terminate()

    def subprocess_poll_end(self):
        log.app(loglvl.STOPPED, f"{self.data.name_} [CB]")

    def video_duration_end(self):
        log.app(loglvl.MAXTIME, f"{self.data.name_} [CB]")

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
        write_pid((self.pid, self.data.name_))

        thread = Thread(target=self.status_subprocess, daemon=True)
        thread.start()

    def status_subprocess(self):
        log.app(loglvl.CAPTURING, f"{self.data.name_} [CB]")
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
        cap_status = query_cap_status(self.data.name_)
        follow, block = cap_status[0]

        if not bool(follow) or bool(block):
            write_remove_pid(self.pid)
            return None

        results = self.get_restart_url((self.max_time, self.data.name_))

        if results is None:
            write_remove_pid(self.pid)
            return None

        if not any("http" in value for value in results):
            write_remove_pid(self.pid)
            return None

        name_, url_ = results

        data = FFmpegData(name_, url_).return_data

        CaptureStreamer(data)

    def get_max_time_url(self, name_):
        url_query = query_url(name_)

        # if url_query is null a bug exist in sql writes for url column
        active_url, *_ = url_query[0]

        return (name_, active_url)

    def get_subprocess_new_url(self, name_):
        results = asyncio.run(self.get_ajax_url([name_]))
        return results

    def get_restart_url(self, data: tuple[bool, str]):
        results: list = []
        max_time, name_ = data

        if max_time:
            return self.get_max_time_url(name_)

        if not max_time:
            sleep(self.delay_)
            results = self.get_subprocess_new_url(name_)

        if not results[0]["url"]:
            log.app(loglvl.STOPPED, f"{name_} [CB] {results[0]['room_status']}")
            return None

        url = results[0]["url"]
        new_data = asyncio.run(self.get_all_m3u8([url]))
        playlist_url, playlist_data = new_data[0]

        streamer_data = process_hls([(playlist_url, playlist_data)])
        new_name, restart_url = streamer_data[0]

        return (new_name, restart_url)

    # async def handle_m3u8(self, data):
    #     name_
    #     hls_urls = await self.get_all_m3u8(new_url)
    #     results = process_hls(hls_urls)
    #     return results
