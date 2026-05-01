-- ============================================================
--  cybereye_schema.sql
--  CyberEye — Weeks 1, 2 & 3  (combined reference file)
--  Engine: SQLite  (file: cyber_eye.db)
--
--  ⚠️  This file is for REFERENCE only.
--      You do NOT need to run it manually.
--      Tables are created automatically when the server starts
--      via init_db() in database.py.
--
--  Share this file with teammates so they can see the full
--  database structure without reading Python code.
-- ============================================================


-- ─────────────────────────────────────────────────────────────
--  TABLE 1: users
--
--  Week 1: id, username, email, created_at
--  Week 2: + password_hash
--  Week 3: unchanged — auth data stays here, profile data is
--           in user_profiles (separate table, see below)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER  PRIMARY KEY AUTOINCREMENT,
    username      TEXT     NOT NULL UNIQUE,
    email         TEXT     NOT NULL UNIQUE,
    password_hash TEXT     NOT NULL,        -- bcrypt hash only, never plain text
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- ─────────────────────────────────────────────────────────────
--  TABLE 2 (NEW — Week 3): user_profiles
--
--  One-to-one with users.  Stores optional display / personal
--  info that does not belong in the auth table.
--
--  The row is created on first profile save — a user can exist
--  without a profile row (profile fields will just be NULL).
--
--  Design note:
--    Keeping profile separate from users means the auth table
--    stays small and fast, and profile columns can grow freely.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_profiles (
    id          INTEGER  PRIMARY KEY AUTOINCREMENT,

    user_id     INTEGER  NOT NULL UNIQUE,       -- UNIQUE enforces one-to-one
    full_name   TEXT,                           -- optional display name
    bio         TEXT,                           -- optional short bio
    avatar_url  TEXT,                           -- optional profile picture URL

    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE                       -- delete profile when user is deleted
);


-- ─────────────────────────────────────────────────────────────
--  TABLE 3: scan_history
--
--  Week 1: user_id, url, result ('safe'|'phishing'), scanned_at
--  Week 2: url → type + input_value; result adds 'suspicious','unknown';
--           scanned_at renamed to timestamp
--  Week 3: + risk_score REAL  (ML model confidence, 0.0–1.0)
--          + notes      TEXT  (human-readable explanation)
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

    -- Week 3 additions ──────────────────────────────────────
    risk_score  REAL     DEFAULT NULL            -- 0.0 = safe, 1.0 = phishing
                CHECK(risk_score IS NULL OR (risk_score >= 0.0 AND risk_score <= 1.0)),
    notes       TEXT     DEFAULT NULL,           -- explanation from ML model

    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE SET NULL                       -- keep scan row if user is deleted
);


-- ─────────────────────────────────────────────────────────────
--  INDEXES
--  Speed up the most common lookups.
-- ─────────────────────────────────────────────────────────────

-- users
CREATE INDEX IF NOT EXISTS idx_user_email      ON users(email);
CREATE INDEX IF NOT EXISTS idx_user_username   ON users(username);

-- user_profiles (Week 3)
CREATE INDEX IF NOT EXISTS idx_profile_user    ON user_profiles(user_id);

-- scan_history
CREATE INDEX IF NOT EXISTS idx_scan_user       ON scan_history(user_id);
CREATE INDEX IF NOT EXISTS idx_scan_time       ON scan_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_scan_result     ON scan_history(result);    -- Week 3: filter by verdict


-- ─────────────────────────────────────────────────────────────
--  SAMPLE DATA  (for testing — remove before production)
-- ─────────────────────────────────────────────────────────────

-- Passwords below are bcrypt hashes of "password123"
INSERT OR IGNORE INTO users (username, email, password_hash) VALUES
    ('alice', 'alice@example.com', '$2b$12$KIX/GRY9h7k3RqPqzV3XBuHash1'),
    ('bob',   'bob@example.com',   '$2b$12$KIX/GRY9h7k3RqPqzV3XBuHash2');

-- Week 3: sample profiles
INSERT OR IGNORE INTO user_profiles (user_id, full_name, bio, avatar_url) VALUES
    (1, 'Alice Smith',   'Cybersecurity student', 'https://example.com/avatars/alice.png'),
    (2, 'Bob Johnson',   NULL,                    NULL);

-- Scan history with Week 3 risk_score + notes
INSERT OR IGNORE INTO scan_history (user_id, type, input_value, result, risk_score, notes) VALUES
    (1,    'url',   'http://free-win-prize.com',  'phishing',   0.97, 'Domain registered 3 days ago; no HTTPS; known phishing pattern.'),
    (1,    'url',   'https://google.com',          'safe',       0.01, NULL),
    (2,    'url',   'http://suspicious-site.xyz',  'suspicious', 0.61, 'Domain age < 30 days; mixed content warnings.'),
    (NULL, 'url',   'https://github.com',          'safe',       0.02, NULL),
    (1,    'phone', '+1-900-555-0199',             'suspicious', 0.55, 'Reported as premium rate scam line.'),
    (2,    'phone', '+1-800-123-4567',             'safe',       0.05, NULL),
    (NULL, 'phone', '00000000',                    'unknown',    NULL, 'Invalid number format; could not classify.');


-- ─────────────────────────────────────────────────────────────
--  USEFUL QUERIES  (backend team reference)
-- ─────────────────────────────────────────────────────────────

-- Get full profile for a logged-in user (joins users + user_profiles)
-- SELECT u.id, u.username, u.email, u.created_at,
--        p.full_name, p.bio, p.avatar_url, p.updated_at
-- FROM users u
-- LEFT JOIN user_profiles p ON p.user_id = u.id
-- WHERE u.id = 1;

-- Get all scans for user 1, newest first
-- SELECT * FROM scan_history WHERE user_id = 1 ORDER BY timestamp DESC;

-- Get only phishing scans with high risk score
-- SELECT * FROM scan_history
-- WHERE result = 'phishing' AND risk_score >= 0.9
-- ORDER BY timestamp DESC;

-- Paginated scan history (page 2, 20 per page)
-- SELECT * FROM scan_history WHERE user_id = 1
-- ORDER BY timestamp DESC LIMIT 20 OFFSET 20;

-- Count total scans per user for stats
-- SELECT user_id, COUNT(*) AS total_scans,
--        SUM(CASE WHEN result = 'phishing' THEN 1 ELSE 0 END) AS phishing_count
-- FROM scan_history WHERE user_id IS NOT NULL
-- GROUP BY user_id;

-- Find user by email (login)
-- SELECT * FROM users WHERE email = 'alice@example.com';

-- Check username availability (signup)
-- SELECT id FROM users WHERE username = 'alice';

-- Verify everything
SELECT * FROM users;
SELECT * FROM user_profiles;
SELECT * FROM scan_history;
