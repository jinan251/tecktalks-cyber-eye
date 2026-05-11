# ============================================================
#  database.py
#  CyberEye — Weeks 1 & 2
#
#  What this file does:
#    Opens the connection to the database and provides a
#    session (think: a temporary workspace) for every request.
#
#  Who uses it:
#    → db_models.py  imports  Base
#    → crud.py       imports  SessionLocal
#    → main.py       imports  init_db, get_db
#
#  Nothing changed between Week 1 and Week 2 in this file.
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ── Database file location ────────────────────────────────────
# Points to cyber_eye.db in the project root folder.
# To switch to PostgreSQL later, just change this one line.
DATABASE_URL = "sqlite:///./cyber_eye.db"

# ── Engine ────────────────────────────────────────────────────
# The engine is the actual connection to the database file.
# check_same_thread=False is required for SQLite + FastAPI.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,   # Change to True to print every SQL query in terminal
)

# ── Session factory ───────────────────────────────────────────
# SessionLocal creates one session per request.
# A session is like a shopping cart — you add/read things,
# then commit (save) or rollback (cancel) at the end.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Base ──────────────────────────────────────────────────────
# Every ORM table class in db_models.py must inherit from Base.
# SQLAlchemy uses Base to track all registered tables.
Base = declarative_base()


# ── FastAPI dependency ────────────────────────────────────────
def get_db():
    """
    Opens a session for one request, then closes it when done.

    FastAPI usage:
        from database import get_db
        from sqlalchemy.orm import Session
        from fastapi import Depends

        @app.post("/scan-link")
        def scan_link(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Table initializer ─────────────────────────────────────────
def init_db():
    """
    Creates all tables in the database if they don't exist yet.
    Call this once when the server starts (in main.py startup).

    Safe to call multiple times — skips tables that already exist.
    """
    from backend.db_models import User, ScanHistory  # noqa: F401
    Base.metadata.create_all(bind=engine)
