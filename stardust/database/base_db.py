from contextlib import asynccontextmanager
from pathlib import Path
import aiosqlite

from config.settings import get_setting

config = get_setting()

DB_FOLDER = config.DB_FOLDER
DB_CONFIG = config.DB_CONFIG


class BaseDB:
    def __init__(self, db_name, **kwargs):
        self.db_name: str = f"{db_name}.sqlite3"
        self.db_Path: Path = DB_FOLDER / self.db_name
        print(self.db_Path)
        self.conn = aiosqlite.connect(self.db_Path)
        print(self.conn)

    @asynccontextmanager
    async def connect(self):
        async with self.conn as conn:
            await conn.executescript(
                """
                PRAGMA mmap_size = 300000000;
                PRAGMA journal_mode=WAL;
                PRAGMA temp_store=MEMORY;
                PRAGMA synchronous=NORMAL;
                PRAGMA cache_size=-10000;
                """
            )

            yield conn

    async def _create_table(self):
        async with self.connect() as conn:
            with open(DB_CONFIG, "r", encoding="utf-8") as file:
                await conn.executescript(file.read())

    async def commit(self):
        await self.conn.commit()

    async def execute(self, query: str, parameters: tuple = ()):
        cursor = await self.conn.cursor()
        if parameters:
            await cursor.execute(query, parameters)
        else:
            await cursor.execute(query)
        return cursor

    async def close(self):
        if self.conn:
            await self.conn.close()

    def __await__(self):
        return self._create_table().__await__()

    async def __aenter__(self):
        await self._create_table()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
