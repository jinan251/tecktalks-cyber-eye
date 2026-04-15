import pyodbc

# ─────────────────────────────────────────────
#  Connection settings — update these to match
#  your SQL Server setup in SSMS
# ─────────────────────────────────────────────
SERVER   = "localhost"          # or your server name shown in SSMS
DATABASE = "CyberEyeDB"
DRIVER   = "ODBC Driver 17 for SQL Server"

# Windows Authentication (most common with SSMS)
CONNECTION_STRING = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
)

# ── If you use SQL Server login instead, comment the line above
#    and uncomment these:
# USERNAME = "your_username"
# PASSWORD = "your_password"
# CONNECTION_STRING = (
#     f"DRIVER={{{DRIVER}}};"
#     f"SERVER={SERVER};"
#     f"DATABASE={DATABASE};"
#     f"UID={USERNAME};"
#     f"PWD={PASSWORD};"
# )


def get_connection():
    return pyodbc.connect(CONNECTION_STRING)


# ─────────────────────────────────────────────
#  Save a scan result
# ─────────────────────────────────────────────
def save_scan(url: str, result: str, user_id: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scan_history (user_id, url, result)
        VALUES (?, ?, ?)
    """, (user_id, url, result))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
#  Get scan history (all or by user)
# ─────────────────────────────────────────────
def get_scan_history(user_id: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("""
            SELECT * FROM scan_history
            WHERE user_id = ?
            ORDER BY scanned_at DESC
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT * FROM scan_history
            ORDER BY scanned_at DESC
        """)
    columns = [col[0] for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return rows


# ─────────────────────────────────────────────
#  Add a user
# ─────────────────────────────────────────────
def add_user(username: str, email: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, email)
        OUTPUT INSERTED.id
        VALUES (?, ?)
    """, (username, email))
    user_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return user_id
