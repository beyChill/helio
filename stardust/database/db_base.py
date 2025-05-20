from pathlib import Path
import sqlite3
from contextlib import contextmanager
from stardust.config.settings import get_db_setting
from stardust.utils.applogging import HelioLogger, loglvl
from stardust.apps import __apps__ as helio_apps

log = HelioLogger()

DB_SQL_FOLDER = get_db_setting().DB_SQL_FOLDER

def get_db_names():
    names = set()
    names.add('helio')
    for app in dir(helio_apps):
        if app.startswith("app_"):
            app_data = getattr(helio_apps, app)
            names.add(app_data[1])
    return names

@contextmanager
def init_connect(file: Path):
    pragma_initial = """
        PRAGMA auto_vacuum = FULL;
        PRAGMA journal_mode = MEMORY;
        PRAGMA temp_store = MEMORY;
        PRAGMA synchronous = OFF;
        PRAGMA cache_size = 1000000;
        PRAGMA foreign_keys = ON;
        pragma integrity_check;
        PRAGMA optimize; 
        ANALYZE; 
        VACUUM;
        """

    with sqlite3.connect(file) as conn:
        conn.executescript(pragma_initial)
        yield conn

def db_init() -> None:
    APP_NAMES = get_db_names()
    DB_FILES=[Path(Path.cwd() / f"stardust/database/db/{name_}.sqlite3") for name_ in APP_NAMES]

    missing_files = {(path.stem, path) for path in DB_FILES if not Path(path).exists()}

    if not missing_files:
        {optimize_db(file) for file in DB_FILES}
        log.info('Databases are ready')
        return None

    {x.parent.mkdir(parents=True, exist_ok=True) for _, x in missing_files}

    try:
        for name_, file in missing_files:
            with init_connect(file) as conn:
                with open(f"{DB_SQL_FOLDER}/{name_}.sql", "r", encoding="utf-8") as file:
                    conn.executescript(file.read())
                log.app(loglvl.CREATED, f"{name_} database")

        log.app(loglvl.SUCCESS, "Database operations complete")
    except sqlite3.OperationalError as e:
        msg = f"{Path(__file__).parts[-1]} {__name__}() {e}"
        log.error(msg)

    return None


def optimize_db(file):
    pragma_optimize = "pragma integrity_check; PRAGMA optimize; ANALYZE; VACUUM;"
    with init_connect(file) as conn:
        conn.executescript(pragma_optimize)
    return None

def display_pragma(sqlite3_connect):
    pragma_query = [
        "PRAGMA auto_vacuum",
        "PRAGMA journal_mode",
        "PRAGMA temp_store",
        "PRAGMA synchronous",
        "PRAGMA wal_autocheckpoint",
        "PRAGMA cache_size",
        "PRAGMA page_size",
        "PRAGMA mmap_size",
        "PRAGMA cache_spill",
        "PRAGMA locking_mode",
        "PRAGMA integrity_check",
    ]
    for pragma in pragma_query:
        query = sqlite3_connect.execute(pragma)
        for value in query:
            print(pragma, "=", value[0])


if __name__ == "__main__":
    db_init()
