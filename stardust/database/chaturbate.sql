CREATE TABLE IF NOT EXISTS chaturbate (
    streamer_name   VARCHAR(30) NOT NULL,
    age             Integer DEFAULT NULL,
    data_total      INTEGER DEFAULT NULL,
    data_review     INTEGER DEFAULT NULL,
    data_keep       INTEGER DEFAULT NULL,
    last_broadcast  DATETIME DEFAULT NULL,
    last_capture    DATETIME DEFAULT NULL,
    seek_capture    DATETIME DEFAULT NULL,
    process_id      INTEGER DEFAULT NULL,
    capture_url     VARCHAR(232) DEFAULT NULL,
    followers       INTEGER DEFAULT NULL,
    viewers         INTEGER DEFAULT NULL,
    most_viewers    INTEGER DEFAULT NULL,
    location_       VARCHAR(40) DEFAULT NULL,
    country         VARCHAR(40) DEFAULT NULL,
    is_new          VARCHAR(6) DEFAULT NULL,
    block_date      DATETIME DEFAULT NULL,
    notes           TEXT,
    tags            TEXT,
    category        VARCHAR(15) DEFAULT NULL,
    bio_chk_date    DATETIME DEFAULT NULL,
    bio_fail_date   DATETIME DEFAULT NULL,
    bio_fail_status INTEGER DEFAULT NULL,
    bio_fail_detail VARCHAR(50) DEFAULT NULL,
    bio_fail_code   VARCHAR(20) DEFAULT NULL,
    created_on      DATETIME DEFAULT (date('now', 'localtime')),
    updated_at      DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
    PRIMARY KEY (streamer_name)
);
CREATE TRIGGER update_chaturbate_updated_at
AFTER
UPDATE ON chaturbate
    WHEN old.updated_at <> (datetime(CURRENT_TIMESTAMP, 'localtime')) BEGIN
UPDATE chaturbate
SET updated_at = (datetime(CURRENT_TIMESTAMP, 'localtime'))
WHERE streamer_name = OLD.streamer_name;
END;

CREATE TRIGGER update_chaturbate_most_viewers
AFTER
INSERT ON chaturbate FOR EACH ROW
    WHEN NEW.most_viewers IS NULL BEGIN
UPDATE chaturbate
SET most_viewers = NEW.viewers
WHERE rowid = NEW.rowid;
END;

CREATE UNIQUE INDEX IF NOT EXISTS idx_streamer ON chaturbate (streamer_name);

