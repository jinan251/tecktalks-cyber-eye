


-- 1. SQLite does not support CREATE DATABASE or USE
-- It works directly with a file (e.g., cybereye.db)

-- 2. Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Scan History Table
CREATE TABLE scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, -- NULL means anonymous scan
    url TEXT NOT NULL,
    result TEXT NOT NULL, -- 'safe' | 'suspicious' | 'phishing'
    scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE SET NULL
);

-- 4. Insert Sample Data
INSERT INTO users (username, email) VALUES
    ('alice', 'alice@example.com'),
    ('bob',   'bob@example.com');

INSERT INTO scan_history (user_id, url, result) VALUES
    (1, 'http://free-win-prize.com', 'phishing'),
    (1, 'https://google.com',        'safe'),
    (2, 'http://suspicious-site.net','suspicious'),
    (NULL, 'https://github.com',     'safe'); -- anonymous scan

-- 5. Verify Data
SELECT * FROM users;
SELECT * FROM scan_history;