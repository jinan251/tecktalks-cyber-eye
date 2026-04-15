-- ============================================================
--  CyberEye Database
--  Run this script in SQL Server Management Studio (SSMS)
-- ============================================================


-- ── 1. Create the Database ───────────────────────────────────
CREATE DATABASE CyberEyeDB;
GO

USE CyberEyeDB;
GO


-- ── 2. Users Table ───────────────────────────────────────────
CREATE TABLE users (
    id          INT           PRIMARY KEY IDENTITY(1,1),
    username    NVARCHAR(100) NOT NULL UNIQUE,
    email       NVARCHAR(255) NOT NULL UNIQUE,
    created_at  DATETIME      NOT NULL DEFAULT GETDATE()
);
GO


-- ── 3. Scan History Table ────────────────────────────────────
CREATE TABLE scan_history (
    id          INT           PRIMARY KEY IDENTITY(1,1),
    user_id     INT           NULL,                          -- NULL = anonymous scan
    url         NVARCHAR(2083) NOT NULL,
    result      NVARCHAR(50)   NOT NULL,                    -- 'safe' | 'suspicious' | 'phishing'
    scanned_at  DATETIME       NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_scan_history_users
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE SET NULL
);
GO


-- ── 4. Test: Insert Sample Data ─────────────────────────────
INSERT INTO users (username, email)
VALUES 
    ('alice', 'alice@example.com'),
    ('bob',   'bob@example.com');
GO

INSERT INTO scan_history (user_id, url, result)
VALUES 
    (1, 'http://free-win-prize.com', 'phishing'),
    (1, 'https://google.com',        'safe'),
    (2, 'http://suspicious-site.net','suspicious'),
    (NULL, 'https://github.com',     'safe');    -- anonymous scan
GO


-- ── 5. Verify Everything ─────────────────────────────────────
SELECT * FROM users;
SELECT * FROM scan_history;
GO
