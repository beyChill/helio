CREATE TABLE IF NOT EXISTS streamer_data(
    streamer_name       VARCHAR(50) NOT NULL COLLATE NOCASE,
    age                 INTEGER DEFAULT NULL,
    last_broadcast      DATETIME DEFAULT NULL,
    location            VARCHAR(30) DEFAULT NULL,
    body_decs           INTEGER DEFAULT NULL,
    is_new              INTEGER DEFAULT NULL,
    followers           INTEGER DEFAULT NULL,
    viewers             INTEGER DEFAULT NULL,
    most_viewers        INTEGER DEFAULT NULL,
    start_dt_utc        INTEGER DEFAULT NULL,
    country             INTEGER DEFAULT NULL,
    tags                TEXT,
    bio_chk_date        DATETIME DEFAULT NULL,
    bio_fail_date       DATETIME DEFAULT NULL,
    bio_fail_status     INTEGER DEFAULT NULL,
    bio_fail_detail     VARCHAR(50) DEFAULT NULL,
    bio_fail_code       VARCHAR(20) DEFAULT NULL,
    created_on          DATETIME DEFAULT (date(CURRENT_TIMESTAMP, 'localtime')),
    updated_at          DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
    PRIMARY KEY (streamer_name)
);

CREATE TRIGGER update_streamer_updated_at
AFTER
UPDATE ON streamer_data
    WHEN old.updated_at <> (datetime(CURRENT_TIMESTAMP, 'localtime')) BEGIN
UPDATE streamer_data
SET updated_at = (datetime(CURRENT_TIMESTAMP, 'localtime'))
WHERE streamer_name = OLD.streamer_name;
END;

CREATE TRIGGER update_streamer_most_viewers
AFTER
INSERT ON streamer_data FOR EACH ROW
    WHEN NEW.most_viewers IS NULL BEGIN
UPDATE streamer_data
SET most_viewers = NEW.viewers
WHERE rowid = NEW.rowid;
END;

CREATE UNIQUE INDEX IF NOT EXISTS idx_streamer ON streamer_data (streamer_name);