from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from threading import Lock
from time import strftime
from typing import Optional

from stardust.config.chroma import rgb
from stardust.config.log_display_setting import connect


class loglvl(Enum):
    NOTSET = 0
    CREATED = 1
    MOVED = 2
    TIMER = 3
    OFFLINE = 8
    STOPPED = 9
    DEBUG = 10
    QUERY = 11
    MAXTIME = 12
    INFO = 20
    SUCCESS = 30
    CAPTURING = 31
    WARNING = 40
    ERROR = 50
    FAILURE = 51


LOG_COLORS = {
    "NOTSET": "",
    "CREATED": "cyan",
    "MOVED": "cyan",
    "TIMER": "royal",
    "OFFLINE": "rust",
    "STOPPED": "yellow",
    "DEBUG": "orange",
    "QUERY": "banana",
    "MAXTIME": "teal",
    "INFO": "glaucous",
    "SUCCESS": "green",
    "CAPTURING": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "FAILURE": "red",
}


class HelioLoggerBase(ABC):
    @abstractmethod
    def query(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def timer(self, msg: str, **kwargs):
        pass

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
    def failure(self, msg: str, **kwargs):
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
        - NOTSET - all messages will show in terminal
        - leave level arg blank as shortcut to NOTSET
    """

    def __init__(
        self,
        log_db: Optional[str] = None,
        *,
        debug=False,
        info=False,
        warning=False,
        error=False,
    ):
        self.log_level = self._set_level(debug, info, warning, error)

        self.log_db = log_db
        self.perms = get_log_perms()
        self.lock=Lock()

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
        "Word appearing in brackets, identifies the log type"
        return rgb(f"[{tag}]:", LOG_COLORS[tag])

    def _msg(self, tag, msg: str):
        return rgb(msg, LOG_COLORS[tag])

    def _level_name(self, level: loglvl):
        return level.name

    def _level_value(self, level: int):
        return loglvl(level).name

    def _msg_level(self, level: str):
        return getattr(loglvl, level)

    def _log(self, level: int, msg: str):
        permission = loglvl(level).name

        if permission not in self.perms:
            return None

        if self.log_level.value > level:
            return None

        if level < loglvl.NOTSET.value:
            print(self._tag(self._level_value(level)), msg)
            return None

        tag = self._tag(self._level_value(level))

        applogger_print(tag, msg,self.lock)

    def app(self, lvl: loglvl, msg: str, **kwargs):
        lvl = getattr(loglvl, lvl.name)
        self.data_format(lvl, msg)

    def timer(self, msg: str, **kwargs):
        level = loglvl.TIMER
        self._log(level.value, self._msg(self._level_name(level), msg), **kwargs)

    def query(self, msg: str, **kwargs):
        level = loglvl.QUERY
        self._log(level.value, self._msg(self._level_name(level), msg), **kwargs)

    def debug(self, msg: str, **kwargs):
        level = loglvl.DEBUG
        self._log(level.value, self._msg(self._level_name(level), msg), **kwargs)

    def info(self, msg: str, **kwargs):
        level = loglvl.INFO
        self._log(level.value, self._msg(self._level_name(level), msg), **kwargs)

    def warning(self, msg: str, **kwargs):
        level = loglvl.WARNING
        self._log(level.value, self._msg(self._level_name(level), msg), **kwargs)

    def failure(self, msg: str, **kwargs):
        level = loglvl.FAILURE
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
    log.query("query")
    log.timer("timer")
    log.info("info")
    log.debug("debug")
    log.error("error")


# @lru_cache(maxsize=None)
def get_log_perms():
    with connect() as conn:
        sql = """
            SELECT value
            FROM log_perm
            WHERE value IS NOT NULL;
        """

        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        data = [x for (x,) in results]
        return data


# @lru_cache(maxsize=None)
def set_permission(level: str, value: str | None):
    with connect() as conn:
        data = (value, level)
        sql = """
            UPDATE log_perm
            SET value = ?
            WHERE level_ = ?
            """
        conn.execute(sql, data)


def applogger_print(tag, msg,lock):
    lock.acquire()
    print(strftime("%H:%M:%S"), tag, msg)
    lock.release()

if __name__ == "__main__":
    set_permission("timer", "TIMER")
    test()
