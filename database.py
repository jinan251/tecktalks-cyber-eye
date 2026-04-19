import pyodbc
import sqlite3
import os

# 1. Flag to switch between SQLite (for you) and SQL Server (for your teammate)
USE_SQL_SERVER = False  # Set this to False to fix your current error

SERVER   = "DESKTOP-29AHSG1" 
DATABASE = "CyberEyeDB"
DRIVER   = "ODBC Driver 17 for SQL Server"

def get_connection():
    if USE_SQL_SERVER:
        connection_string = f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"
        return pyodbc.connect(connection_string)
    else:
        # Connect to SQLite (Local file)
        db_path = os.path.join(os.path.dirname(__file__), "cyber_eye.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

# 2. Automatically create the tables in SQLite if they don't exist
if not USE_SQL_SERVER:
    conn = get_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS scan_history 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, url TEXT, result TEXT, scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT)''')
    conn.commit()
    conn.close()

# 3. Database functions
def save_scan(url: str, result: str, user_id: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scan_history (user_id, url, result) VALUES (?, ?, ?)", (user_id, url, result))
    conn.commit()
    conn.close()

def add_user(username: str, email: str):
    conn = get_connection()
    cursor = conn.cursor()
    if USE_SQL_SERVER:
        cursor.execute("INSERT INTO users (username, email) OUTPUT INSERTED.id VALUES (?, ?)", (username, email))
        user_id = cursor.fetchone()[0]
    else:
        cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, email))
        user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_scan_history(user_id: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM scan_history " + ("WHERE user_id = ? " if user_id else "") + "ORDER BY scanned_at DESC"
    if user_id: cursor.execute(query, (user_id,))
    else: cursor.execute(query)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows