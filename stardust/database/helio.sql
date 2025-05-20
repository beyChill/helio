CREATE TABLE IF NOT EXISTS helio (
    streamer_name   VARCHAR(50) NOT NULL,
    slug            VARCHAR(5) NOT NULL,
    last_broadcast  DATETIME DEFAULT NULL,
    data_total      INTEGER DEFAULT NULL,
    data_review     INTEGER DEFAULT NULL,
    data_keep       INTEGER DEFAULT NULL,
    last_capture    DATETIME DEFAULT NULL,
    seek_capture    DATETIME DEFAULT NULL,
    process_id      INTEGER DEFAULT NULL,
    capture_url     TEXT DEFAULT NULL,
    http_code       INTEGER DEFAULT NULL,
    http_text       TEXT DEFAULT NULL,
    block_date      DATETIME DEFAULT NULL,
    notes           TEXT,
    category        VARCHAR(15) DEFAULT NULL,
    created_on      DATETIME DEFAULT (date(CURRENT_TIMESTAMP, 'localtime')),
    updated_at      DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
    PRIMARY KEY (streamer_name, slug)
);
CREATE TRIGGER helio_updated_at
AFTER
UPDATE ON helio
    WHEN old.updated_at <> (datetime(CURRENT_TIMESTAMP, 'localtime')) 
BEGIN UPDATE helio
SET updated_at = (datetime(CURRENT_TIMESTAMP, 'localtime'))
WHERE streamer_name = OLD.streamer_name;
END;

CREATE TRIGGER update_helio_last_broadcast
AFTER
INSERT ON helio FOR EACH ROW
    WHEN NEW.last_broadcast IS NULL BEGIN
UPDATE helio
SET last_broadcast = NEW.last_broadcast
WHERE rowid = NEW.rowid;
END;

CREATE UNIQUE INDEX IF NOT EXISTS idx_helio ON helio (streamer_name, slug);