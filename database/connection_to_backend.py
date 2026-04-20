import sqlite3
import os

# Set this to False to ensure SQLite is used (fixing SSMS errors)
USE_SQL_SERVER = False  

def get_connection():
    if USE_SQL_SERVER:
        # Configuration for SQL Server (Teammate's environment)
        SERVER = "DESKTOP-29AHSG1" 
        DATABASE = "CyberEyeDB"
        DRIVER = "ODBC Driver 17 for SQL Server"
        connection_string = f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"
        import pyodbc
        return pyodbc.connect(connection_string)
    else:
        # Use SQLite for your environment
        # BASE_DIR points to 'tecktalks-cyber-eye' root folder
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(BASE_DIR, "cyber_eye.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

# Automatically create tables if using SQLite
if not USE_SQL_SERVER:
    conn = get_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS scan_history 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, url TEXT, result TEXT, scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT)''')
    conn.commit()
    conn.close()

def save_scan(url: str, result: str, user_id: int = None):
    """Saves the scan results into the database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scan_history (user_id, url, result) VALUES (?, ?, ?)", (user_id, url, result))
    conn.commit()
    conn.close()