CREATE TABLE IF NOT EXISTS myfreecams (
    streamer_name   VARCHAR(30) NOT NULL COLLATE NOCASE,
    last_broadcast  DATETIME DEFAULT NULL,
    data_total      INTEGER DEFAULT NULL,
    data_review     INTEGER DEFAULT NULL,
    data_keep       INTEGER DEFAULT NULL,
    last_capture    DATETIME DEFAULT NULL,
    seek_capture    DATETIME DEFAULT NULL,
    process_id      INTEGER DEFAULT NULL,
    capture_url     VARCHAR(232) DEFAULT NULL,
    block_date      DATETIME DEFAULT NULL,
    notes           TEXT,
    category        VARCHAR(15) DEFAULT NULL,
    created_on      DATETIME DEFAULT (date('now', 'localtime')),
    updated_at      DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
    PRIMARY KEY (streamer_name)
);

CREATE TRIGGER update_myfreecams_updated_at
AFTER
UPDATE ON myfreecams
    WHEN old.updated_at <> (datetime(CURRENT_TIMESTAMP, 'localtime')) BEGIN
UPDATE myfreecams
SET updated_at = (datetime(CURRENT_TIMESTAMP, 'localtime'))
WHERE streamer_name = OLD.streamer_name;
END;

CREATE TRIGGER update_myfreecams_last_broadcast
AFTER
INSERT ON myfreecams FOR EACH ROW
    WHEN NEW.last_broadcast IS NULL BEGIN
UPDATE myfreecams
SET last_broadcast = NEW.last_broadcast
WHERE rowid = NEW.rowid;
END;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mfc ON myfreecams (streamer_name);

CREATE TABLE IF NOT EXISTS streamer_data(
    streamer_name VARCHAR(30) NOT NULL COLLATE NOCASE,
    creation    INTEGER DEFAULT NULL,
    followers       INTEGER DEFAULT NULL,
    viewers         INTEGER DEFAULT NULL,
    most_viewers    INTEGER DEFAULT NULL,
    is_new      INTEGER DEFAULT NULL,
    missmfc     INTEGER DEFAULT NULL,
    camscore    INTEGER DEFAULT NULL,
    continent   VARCHAR(30) DEFAULT NULL,
    country     VARCHAR(4) DEFAULT NULL,
    rank_       INTEGER DEFAULT NULL,
    rc          INTEGER DEFAULT NULL,
    tags        TEXT,
    bio_chk_date    DATETIME DEFAULT NULL,
    bio_fail_date   DATETIME DEFAULT NULL,
    bio_fail_status INTEGER DEFAULT NULL,
    bio_fail_detail VARCHAR(50) DEFAULT NULL,
    bio_fail_code   VARCHAR(20) DEFAULT NULL,
    created_on  DATETIME DEFAULT (date('now', 'localtime')),
    updated_at  DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
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
CREATE UNIQUE INDEX IF NOT EXISTS idx_streamer ON streamer_data (streamer_name);


CREATE TABLE IF NOT EXISTS url_data (
    streamer_name   VARCHAR(30) NOT NULL COLLATE NOCASE,
    sid_            INTEGER DEFAULT NULL,
    uid_            INTEGER DEFAULT NULL,
    vs              INTEGER DEFAULT NULL,
    pid             INTEGER DEFAULT NULL,
    lv              INTEGER DEFAULT NULL,
    camserv         INTEGER DEFAULT NULL,
    phase           VARCHAR(5) DEFAULT NULL,
    updated_at      DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
    PRIMARY KEY (streamer_name)
);

CREATE TRIGGER update_url_data_updated_at
AFTER
UPDATE ON url_data
    WHEN old.updated_at <> (datetime(CURRENT_TIMESTAMP, 'localtime')) BEGIN
UPDATE url_data
SET updated_at = (datetime(CURRENT_TIMESTAMP, 'localtime'))
WHERE streamer_name = OLD.streamer_name;
END;

CREATE UNIQUE INDEX IF NOT EXISTS idx_url ON url_data (streamer_name);