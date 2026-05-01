# ============================================================
#  db_models.py
#  CyberEye — Weeks 1 & 2
#
#  What this file does:
#    Defines the database tables as Python classes.
#    SQLAlchemy reads these classes and creates the actual
#    SQL tables in cyber_eye.db automatically.
#
#  Who uses it:
#    → crud.py  imports  User, ScanHistory, ScanType, ScanResult
#    → database.py  imports  User, ScanHistory  (inside init_db)
#
#  Imports from:
#    ← database.py  (Base)
# ============================================================

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from sqlalchemy import Boolean

from database import Base   # ← comes from database.py


# ════════════════════════════════════════════════════════════
#  ENUMS
#  These are allowed values enforced at the Python level.
#  If you pass a value not in the enum, it raises an error
#  before anything reaches the database.
# ════════════════════════════════════════════════════════════

# ── Added in Week 2 ──────────────────────────────────────────
class ScanType(str, enum.Enum):
    """What kind of thing was scanned."""
    url   = "url"     # a website link
    phone = "phone"   # a phone number

# ── Added in Week 2 (Week 1 only had 'safe' and 'phishing') ──
class ScanResult(str, enum.Enum):
    """The final verdict of a scan."""
    safe       = "safe"
    suspicious = "suspicious"
    phishing   = "phishing"
    unknown    = "unknown"   # used when phone scan result is unclear


# ════════════════════════════════════════════════════════════
#  TABLE 1: users
#  One row = one registered user account.
# ════════════════════════════════════════════════════════════
class User(Base):
    __tablename__ = "users"

    # ── Week 1 columns ───────────────────────────────────────
    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username   = Column(String(100), unique=True, nullable=False, index=True)
    email      = Column(String(200), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    #testing 
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True, unique=True)
    token_expiry = Column(Integer, nullable=True) # Changed from DateTime to Integer

    # ── Week 2 addition ──────────────────────────────────────
    # Stores the bcrypt hash of the password — NEVER the real password.
    # The backend hashes it before calling crud.create_user().
    # Example hash: "$2b$12$KIX/GRY9h7k3RqPq..."
    password_hash = Column(String(255), nullable=False)

    # ── Relationship ─────────────────────────────────────────
    # Lets you access all scans for a user directly in Python:
    #   user.scans  →  list of ScanHistory rows
    scans = relationship(
        "ScanHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"


# ════════════════════════════════════════════════════════════
#  TABLE 2: scan_history
#  One row = one completed scan (URL or phone number).
#  user_id can be NULL — that means the scan was anonymous
#  (done by someone who is not logged in).
# ════════════════════════════════════════════════════════════
class ScanHistory(Base):
    __tablename__ = "scan_history"

    # ── Week 1 columns ───────────────────────────────────────
    id      = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
                Integer,
                ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,    # NULL = anonymous scan, allowed
                index=True,
              )
    result  = Column(Enum(ScanResult), nullable=False)   # final verdict

    # ── Week 2 additions ─────────────────────────────────────
    # Week 1 had a column called 'url' (URL only).
    # Week 2 replaced it with two columns so one table handles
    # both URL scans and phone scans:
    #
    #   type        →  'url' or 'phone'
    #   input_value →  the actual URL or phone number
    #
    type        = Column(Enum(ScanType), nullable=False)
    input_value = Column(Text, nullable=False)

    # ── Week 1 column (renamed in Week 2 for clarity) ────────
    # Was called 'scanned_at' in Week 1, renamed to 'timestamp'
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # ── Relationship ─────────────────────────────────────────
    # Lets you access the user who made this scan:
    #   scan.user  →  User object (or None if anonymous)
    user = relationship("User", back_populates="scans")

    def __repr__(self):
        return (
            f"<ScanHistory id={self.id} "
            f"type={self.type} "
            f"result={self.result} "
            f"input={str(self.input_value)[:30]!r}>"
        )
