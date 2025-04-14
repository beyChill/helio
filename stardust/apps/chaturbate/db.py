from database.base_db import BaseDB


class AsyncStreamerCB(BaseDB):


    def __init__(self):
        self.db_name="chaturbate"
        super().__init__(self.db_name)
    async def _create_table(self):
        await super()._create_table()

        fields = [
            "streamer_name   VARCHAR(30) NOT NULL",
            "age             Integer DEFAULT NULL",
            "data_total      INTEGER DEFAULT NULL",
            "data_review     INTEGER DEFAULT NULL",
            "data_kept       INTEGER DEFAULT NULL",
            "last_broadcast  DATETIME DEFAULT NULL",
            "last_capture    DATETIME DEFAULT NULL",
            "seek_capture    DATETIME DEFAULT NULL",
            "pid             INTEGER DEFAULT NULL",
            # url_            VARCHAR(212) DEFAULT NULL,
            # followers       INTEGER DEFAULT NULL,
            # viewers         INTEGER DEFAULT NULL,
            # most_viewers    INTEGER DEFAULT NULL,
            # location_       VARCHAR(40) DEFAULT NULL,
            # country         VARCHAR(40) DEFAULT NULL,
            # is_new          VARCHAR(6) DEFAULT NULL,
            # block_date      DATETIME DEFAULT NULL,
            # notes           TEXT,
            # tags            TEXT,
            # capture_status  VARCHAR(15) DEFAULT NULL,
            # bio_chk_date    DATETIME DEFAULT NULL,
            # bio_fail_date   DATETIME DEFAULT NULL,
            # bio_fail_code   INTEGER DEFAULT 0,
            # bio_fail_text   VARCHAR(50) DEFAULT NULL,
            # created_on      DATETIME DEFAULT (date('now','localtime')),
            # updated_at      DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP,'localtime')),
            "PRIMARY KEY (streamer_name)",
        ]

        fields_sql = ", ".join(fields)
        # await self.execute(f"""
        #     CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} ({fields_sql})
        #     """)

    def cool(self):
        pass
