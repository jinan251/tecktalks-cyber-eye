-- ─────────────────────────────────────────────────────────────
--  TABLE 1: users
--
--  Week 1: id, username, email, created_at
--  Week 2: + password_hash
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER  PRIMARY KEY AUTOINCREMENT,
    username      TEXT     NOT NULL UNIQUE,
    email         TEXT     NOT NULL UNIQUE,
    password_hash TEXT     NOT NULL,        -- bcrypt hash only, never plain text
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- ─────────────────────────────────────────────────────────────
--  TABLE 2: scan_history
--
--  Week 1: user_id, url (TEXT), result ('safe'|'phishing'), scanned_at
--  Week 2: url column split into → type ('url'|'phone') + input_value
--          result now includes 'suspicious' and 'unknown'
--          scanned_at renamed to timestamp
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS scan_history (
    id          INTEGER  PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER  DEFAULT NULL,           -- NULL = anonymous scan (allowed)
    type        TEXT     NOT NULL
                CHECK(type   IN ('url', 'phone')),
    input_value TEXT     NOT NULL,               -- the URL or phone number
    result      TEXT     NOT NULL
                CHECK(result IN ('safe', 'suspicious', 'phishing', 'unknown')),
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE SET NULL                       -- if user deleted, keep scan row (user_id → NULL)
);


-- ─────────────────────────────────────────────────────────────
--  INDEXES  (Week 2)
--  Speed up the most common lookups.
-- ─────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_user_email    ON users(email);
CREATE INDEX IF NOT EXISTS idx_user_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_scan_user     ON scan_history(user_id);
CREATE INDEX IF NOT EXISTS idx_scan_time     ON scan_history(timestamp DESC);


-- ─────────────────────────────────────────────────────────────
--  SAMPLE DATA  (for testing — remove before production)
-- ─────────────────────────────────────────────────────────────

-- Passwords below are bcrypt hashes of "password123"
INSERT OR IGNORE INTO users (username, email, password_hash) VALUES
    ('alice', 'alice@example.com', '$2b$12$KIX/GRY9h7k3RqPqzV3XBuHash1'),
    ('bob',   'bob@example.com',   '$2b$12$KIX/GRY9h7k3RqPqzV3XBuHash2');

INSERT OR IGNORE INTO scan_history (user_id, type, input_value, result) VALUES
    -- URL scans
    (1,    'url',   'http://free-win-prize.com',  'phishing'),
    (1,    'url',   'https://google.com',          'safe'),
    (2,    'url',   'http://suspicious-site.xyz',  'suspicious'),
    (NULL, 'url',   'https://github.com',          'safe'),       -- anonymous
    -- Phone scans (Week 2)
    (1,    'phone', '+1-900-555-0199',             'suspicious'),
    (2,    'phone', '+1-800-123-4567',             'safe'),
    (NULL, 'phone', '00000000',                    'unknown');   -- anonymous


-- ─────────────────────────────────────────────────────────────
--  USEFUL QUERIES  (backend team reference)
-- ─────────────────────────────────────────────────────────────

-- Get all scans for user with id = 1
-- SELECT * FROM scan_history WHERE user_id = 1 ORDER BY timestamp DESC;

-- Get only phone scans
-- SELECT * FROM scan_history WHERE type = 'phone' ORDER BY timestamp DESC;

-- Count results by type
-- SELECT result, COUNT(*) FROM scan_history GROUP BY result;

-- Find user by email (used in login)
-- SELECT * FROM users WHERE email = 'alice@example.com';

-- Check if username is taken (used in signup)
-- SELECT id FROM users WHERE username = 'alice';

-- Verify everything
SELECT * FROM users;
SELECT * FROM scan_history;
