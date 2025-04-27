CREATE TABLE IF NOT EXISTS camsoda (
    streamer_name VARCHAR(30) NOT NULL,
    PRIMARY KEY (streamer_name)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_streamer ON camsoda (streamer_name);
