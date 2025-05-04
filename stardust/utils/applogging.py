from abc import ABC, abstractmethod
from dataclasses import dataclass

from time import strftime
from typing import Optional

# from chroma import rgb
from stardust.config.chroma import rgb

# from config.settings import get_setting
from enum import Enum

class loglvl(Enum):
    NOTSET = 0
    CREATED = 1
    MOVED = 2
    STOPPED = 9
    DEBUG = 10
    MAXTIME = 12
    INFO = 20
    SUCCESS = 30
    CAPTURING = 31
    WARNING = 40
    ERROR = 50
    FAILURE = 51


_levelToName = {
    loglvl.NOTSET: "NOTSET",
    loglvl.CREATED: "CREATED",
    loglvl.MOVED: "MOVED",
    loglvl.STOPPED: "STOPPED",
    loglvl.DEBUG: "DEBUG",
    loglvl.MAXTIME: "MAXTIME",
    loglvl.INFO: "INFO",
    loglvl.SUCCESS: "SUCCESS",
    loglvl.CAPTURING: "CAPTURING",
    loglvl.WARNING: "WARNING",
    loglvl.ERROR: "ERROR",
    loglvl.FAILURE: "FAILURE",
}

_valueToName = {
    loglvl.NOTSET.value: "NOTSET",
    loglvl.CREATED.value: "CREATED",
    loglvl.MOVED.value: "MOVED",
    loglvl.STOPPED.value: "STOPPED",
    loglvl.DEBUG.value: "DEBUG",
    loglvl.SUCCESS.value: "SUCCESS",
    loglvl.MAXTIME.value: "MAXTIME",
    loglvl.INFO.value: "INFO",
    loglvl.CAPTURING.value: "CAPTURING",
    loglvl.WARNING.value: "WARNING",
    loglvl.ERROR.value: "ERROR",
    loglvl.FAILURE.value: "FAILURE",
}

_msgToLevel = {
    "NOTSET": loglvl.NOTSET,
    "CREATED": loglvl.CREATED,
    "MOVED": loglvl.MOVED,
    "STOPPED": loglvl.STOPPED,
    "DEBUG": loglvl.DEBUG,
    "SUCCESS": loglvl.SUCCESS,
    "MAXTIME": loglvl.MAXTIME,
    "INFO": loglvl.INFO,
    "CAPTURING": loglvl.CAPTURING,
    "WARNING": loglvl.WARNING,
    "ERROR": loglvl.ERROR,
    "FAILURE": loglvl.FAILURE,
}

LOG_COLORS = {
    "NOTSET": "",
    "CREATED": "cyan",
    "MOVED": "cyan",
    "STOPPED": "yellow",
    "DEBUG": "orange",
    "SUCCESS": "green",
    "MAXTIME": "teal",
    "INFO": "white",
    "CAPTURING": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "FAILURE": "red",
}


class HelioLoggerBase(ABC):
    @abstractmethod
    def debug(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def info(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def warning(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def error(self, msg: str | Exception, **kwargs):
        pass

    @abstractmethod
    def app(self, lvl: loglvl, msg: str, **kwargs):
        pass


@dataclass(slots=True)
class HelioLogger(HelioLoggerBase):
    """
    Custom logger for custom event formating and printing
        - low budget logger not replacement for builtin
        - NOTSET allows display of all messages in the terminal. All messages will show in terminal
        - leave level arg blank as shortcut to NOTSET
    """

    def __init__(
        self,
        # log_level: loglvl = loglvl.NOTSET,
        log_db: Optional[str] = None,
        *,
        debug=False,
        info=False,
        warning=False,
        error=False,
    ):
        # self.label: Optional[str] = None
        self.log_level = self._set_level(debug, info, warning, error)

        self.log_db = log_db

        # if self.log_db:
        #     try:
        #         db_path = get_db_setting().DB_FOLDER
        #         if not db_path.exists():
        #             db_path.exists()

        #     except Exception as e:
        #         print(e)

    def _set_level(self, *args):
        custom_level = [name for name, value in locals().items() if value is True]

        if len(custom_level) > 1:
            last_level_entry = self._msg_level(custom_level[-1].upper())
            return last_level_entry

        if custom_level:
            new_level = self._msg_level(custom_level[0].upper())
            return new_level

        return loglvl.NOTSET

    def _tag(self, tag: str) -> str:
        "Word appearing in brackets, identifies the message level"
        return rgb(f"[{tag}]:", LOG_COLORS[tag])

    def _msg(self, tag, msg: str):
        return rgb(msg, LOG_COLORS[tag])

    def _level_name(self, level: loglvl):
        return _levelToName[level]

    def _level_value(self, level: int):
        return _valueToName[level]

    def _msg_level(self, level: str):
        return _msgToLevel[level.upper()]

    def _log(self, level: int, msg: str):
        if self.log_level.value > level:
            return None

        if level < loglvl.NOTSET.value:
            print(self._tag(self._level_value(level)), msg)
            return None

        print(
            strftime("%H:%M:%S"), self._tag(self._level_value(level)), msg, flush=True
        )

    def app(self, lvl: loglvl, msg: str, **kwargs):
        lvl = _msgToLevel[lvl.name]
        self.data_format(lvl, msg)

    def debug(self, msg: str, **kwargs):
        level = loglvl.DEBUG
        self._log(level.value, self._msg(self._level_name(level), msg), **kwargs)

    def info(self, msg: str, **kwargs):
        level = loglvl.INFO
        self._log(level.value, self._msg(self._level_name(level), msg), **kwargs)

    def warning(self, msg: str, **kwargs):
        level = loglvl.WARNING
        self._log(level.value, self._msg(self._level_name(level), msg), **kwargs)

    def error(self, msg: str | Exception, **kwargs):
        level = loglvl.ERROR
        msg = str(msg)
        self._log(level.value, self._msg(self._level_name(level), msg), **kwargs)

    def data_format(self, level: loglvl, msg: str):
        self._log(level.value, self._msg(self._level_name(level), msg))


def test():
    log = HelioLogger(warning=True)
    log.app(loglvl.CREATED, "created")
    log.app(loglvl.STOPPED, "stopped")
    log.app(loglvl.MAXTIME, "maxtime")
    log.debug("debug")
    log.error("error")


if __name__ == "__main__":
    test()
