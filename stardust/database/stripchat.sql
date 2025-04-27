CREATE TABLE IF NOT EXISTS stripchat (
    streamer_name VARCHAR(30) NOT NULL,
    PRIMARY KEY (streamer_name)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_streamer ON stripchat (streamer_name);
