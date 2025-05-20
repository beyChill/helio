CREATE TABLE IF NOT EXISTS stripchat (
    streamer_name   VARCHAR(50) NOT NULL,
    last_broadcast  DATETIME DEFAULT NULL,
    data_total      INTEGER DEFAULT NULL,
    data_review     INTEGER DEFAULT NULL,
    data_keep       INTEGER DEFAULT NULL,
    last_capture    DATETIME DEFAULT NULL,
    seek_capture    DATETIME DEFAULT NULL,
    process_id      INTEGER DEFAULT NULL,
    capture_url     TEXT DEFAULT NULL,
    block_date      DATETIME DEFAULT NULL,
    notes           TEXT,
    category        VARCHAR(15) DEFAULT NULL,
    created_on      DATETIME DEFAULT (date(CURRENT_TIMESTAMP, 'localtime')),
    updated_at      DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
    PRIMARY KEY (streamer_name)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_streamer ON stripchat (streamer_name);
