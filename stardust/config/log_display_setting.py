import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB = Path(Path(__file__).parent / "log_permissions.sqlite3")


@contextmanager
def connect():
    pragma_initial = """
        PRAGMA auto_vacuum = FULL;
        PRAGMA journal_mode = MEMORY;
        PRAGMA temp_store = MEMORY;
        PRAGMA synchronous = OFF;
        pragma integrity_check;
        PRAGMA optimize; 
        ANALYZE; 
        VACUUM;
        """

    with sqlite3.connect(DB) as conn:
        conn.executescript(pragma_initial)
        yield conn


def log_permissions_init():
    if not DB.exists():
        sqls = """
            CREATE TABLE IF NOT EXISTS log_perm (
            level_     VARCHAR(20) NOT NULL ,
            value      VARCHAR(6) DEFAULT NULL,
            PRIMARY KEY (level_)
            );
            INSERT INTO log_perm
                (level_, value)
            VALUES 
                ("notset", NULL),	
                ("created", "CREATED"),
                ("moved", NULL),
                ("timer", "TIMER"),
                ("offline", NULL),
                ("stopped", NULL),
                ("debug", NULL),
                ("query", "QUERY"),
                ("maxtime", NULL),
                ("info", "INFO"),
                ("success", NULL),
                ("capturing", "CAPTURING"),
                ("warning", NULL),
                ("error", "ERROR"),
                ("failure", "FAILURE");
            """
        try:
            with connect() as conn:
                conn.executescript(sqls)
        except sqlite3.OperationalError as e:
            print(e)


if __name__ == "__main__":
    log_permissions_init()
