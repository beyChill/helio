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
    "MOVED": "maroon",
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
    "FAILURE": "rose",
}


@lru_cache
def get_db_perms():
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


def set_permission(level: str, value: str | None):
    get_db_perms.cache_clear()
    with connect() as conn:
        data = (value, level)
        sql = """
            UPDATE log_perm
            SET value = ?
            WHERE level_ = ?
            """
        conn.execute(sql, data)


class HelioLogger:
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

    def _set_level(self, *args, **kwargs):
        custom_level = [name for name, value in locals().items() if value is True]

        if len(custom_level) > 1:
            last_level_entry = self._msg_level(custom_level[-1].upper())
            return last_level_entry

        if custom_level:
            new_level = self._msg_level(custom_level[0].upper())
            return new_level

        return loglvl.NOTSET

    def _color_msg(self, msg: str, tag):
        return rgb(msg, LOG_COLORS[tag])

    def _msg_level(self, level: str):
        return getattr(loglvl, level)

    def _tag(self, tag: str) -> str:
        "Word appearing in brackets, identifies the log type"
        return rgb(f"[{tag}]:", LOG_COLORS[tag])

    def _log(self, level: loglvl, msg: str, *args, **kwargs):
        tag = self._tag(level.name)
        msg_color = self._color_msg(msg, level.name)

        logger_print(tag, msg_color)

    def handle_level(self, level: loglvl, msg: str, *args, **kwargs):
        if self.isPrintable(level):
            self._log(level, msg, *args, **kwargs)

    def isPrintable(self, level: loglvl):
        perms = get_db_perms()
        if level.name not in perms:
            return None

        if level.value < self.log_level.value:
            return None

        return True


base = HelioLogger()


def created(msg, *args, **kwargs):
    base.handle_level(loglvl.CREATED, msg, *args, **kwargs)


def moved(msg, *args, **kwargs):
    base.handle_level(loglvl.MOVED, msg, *args, **kwargs)


def timer(msg, *args, **kwargs):
    base.handle_level(loglvl.TIMER, msg, *args, **kwargs)


def offline(msg, *args, **kwargs):
    base.handle_level(loglvl.OFFLINE, msg, *args, **kwargs)


def stopped(msg, *args, **kwargs):
    base.handle_level(loglvl.STOPPED, msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    base.handle_level(loglvl.DEBUG, msg, *args, **kwargs)


def query(msg, *args, **kwargs):
    base.handle_level(loglvl.QUERY, msg, *args, **kwargs)


def maxtime(msg, *args, **kwargs):
    base.handle_level(loglvl.MAXTIME, msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    base.handle_level(loglvl.INFO, msg, *args, **kwargs)


def success(msg, *args, **kwargs):
    base.handle_level(loglvl.SUCCESS, msg, *args, **kwargs)


def capturing(msg, *args, **kwargs):
    base.handle_level(loglvl.CAPTURING, msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    base.handle_level(loglvl.WARNING, msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    base.handle_level(loglvl.ERROR, msg, *args, **kwargs)


def failure(msg, *args, **kwargs):
    base.handle_level(loglvl.FAILURE, msg, *args, **kwargs)


def logger_print(tag, msg):
    lock = Lock()
    with lock:
        print(strftime("%H:%M:%S"), tag, msg, flush=True)
