CREATE TABLE IF NOT EXISTS myfreecams (
    streamer_name VARCHAR(30) NOT NULL,
    sid         INTEGER DEFAULT NULL,
    uid         INTEGER DEFAULT NULL,
    vs          INTEGER DEFAULT NULL,
    pid         INTEGER DEFAULT NULL,
    lv          INTEGER DEFAULT NULL,
    camserv     INTEGER DEFAULT NULL,
    phase       VARCHAR(5) DEFAULT NULL,
    chat_color  VARCHAR(8) DEFAULT NULL,
    chat_font   INTEGER(232) DEFAULT NULL,
    chat_opt    INTEGER DEFAULT NULL,
    creation    INTEGER DEFAULT NULL,
    avatar      INTEGER DEFAULT NULL,
    profile_    INTEGER DEFAULT NULL,
    photos      INTEGER DEFAULT NULL,
    blurb       VARCHAR(200) DEFAULT NULL,
    is_new      INTEGER DEFAULT NULL,
    missmfc     INTEGER DEFAULT NULL,
    camscore    INTEGER DEFAULT NULL,
    country     VARCHAR(4) DEFAULT NULL,
    rank_       INTEGER DEFAULT NULL,
    rc          INTEGER DEFAULT NULL,
    topic       INTEGER DEFAULT NULL,
    hidecs      VARCHAR(200) DEFAULT NULL,
    share_albums INTEGER DEFAULT NULL,
    share_follows INTEGER DEFAULT NULL,
    share_clubs INTEGER DEFAULT NULL,
    share_tm_album INTEGER DEFAULT NULL,
    share_collections INTEGER DEFAULT NULL,
    share_stores INTEGER DEFAULT NULL,
    share_goals INTEGER DEFAULT NULL,
    share_polls INTEGER DEFAULT NULL,
    share_things INTEGER DEFAULT NULL,
    share_recent_album_tm INTEGER DEFAULT NULL,
    share_recent_club_tm INTEGER DEFAULT NULL,
    share_recent_collection_tm INTEGER DEFAULT NULL,
    share_recent_goal_tm INTEGER DEFAULT NULL,
    share_recent_item_tm INTEGER DEFAULT NULL,
    share_recent_poll_tm INTEGER DEFAULT NULL,
    share_recent_story_tm INTEGER DEFAULT NULL,
    share_recent_album_thumb VARCHAR(80) DEFAULT NULL,
    share_recent_club_thumb VARCHAR(80) DEFAULT NULL,
    share_recent_collection_thumb VARCHAR(80) DEFAULT NULL,
    share_recent_goal_thumb VARCHAR(80) DEFAULT NULL,
    share_recent_item_thumb VARCHAR(80) DEFAULT NULL,
    share_recent_poll_thumb VARCHAR(80) DEFAULT NULL,
    share_recent_story_thumb VARCHAR(80) DEFAULT NULL,
    share_recent_album_title VARCHAR(80) DEFAULT NULL,
    share_recent_club_title VARCHAR(80) DEFAULT NULL,
    share_recent_collection_title VARCHAR(80) DEFAULT NULL,
    share_recent_goal_title VARCHAR(80) DEFAULT NULL,
    share_recent_item_title VARCHAR(80) DEFAULT NULL,
    share_recent_poll_title VARCHAR(80) DEFAULT NULL,
    share_recent_story_title VARCHAR(80) DEFAULT NULL,
    share_recent_album_slug INTEGER DEFAULT NULL,
    share_recent_collection_slug VARCHAR(80) DEFAULT NULL,
    share_tipmenus INTEGER DEFAULT NULL,
    share_recordings INTEGER DEFAULT NULL,
    share_free_albums INTEGER DEFAULT NULL,
    social_uname INTEGER DEFAULT NULL,
    social_posts INTEGER DEFAULT NULL,
    social_tm_post INTEGER DEFAULT NULL,
    last_broadcast DATETIME DEFAULT NULL,
    data_review INTEGER DEFAULT NULL,
    data_keep INTEGER DEFAULT NULL,
    data_total INTEGER DEFAULT NULL,
    last_capture DATETIME DEFAULT NULL,
    seek_capture DATETIME DEFAULT NULL,
    pid_ INTEGER DEFAULT NULL,
    url_ VARCHAR(232) DEFAULT NULL,
    followers INTEGER DEFAULT NULL,
    viewers INTEGER DEFAULT NULL,
    most_viewers INTEGER DEFAULT NULL,
    block_date DATETIME DEFAULT NULL,
    notes TEXT,
    tags TEXT,
    category VARCHAR(15) DEFAULT NULL,
    bio_chk_date DATETIME DEFAULT NULL,
    bio_fail_date DATETIME DEFAULT NULL,
    bio_fail_status INTEGER DEFAULT NULL,
    bio_fail_detail VARCHAR(50) DEFAULT NULL,
    bio_fail_code VARCHAR(20) DEFAULT NULL,
    created_on DATETIME DEFAULT (date('now', 'localtime')),
    updated_at DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
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

CREATE TRIGGER update_myfreecams_most_viewers
AFTER
INSERT ON myfreecams FOR EACH ROW
    WHEN NEW.last_broadcast IS NOT NULL BEGIN
UPDATE myfreecams
SET last_broadcast = NEW.last_broadcast
WHERE rowid = NEW.rowid;
END;

CREATE UNIQUE INDEX IF NOT EXISTS idx_streamer ON myfreecams (streamer_name);

