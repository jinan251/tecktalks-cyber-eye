# ============================================================
#  db_models.py
#  CyberEye 
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

from backend.database import Base   # ← comes from database.py


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

    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,          # one-to-one: returns a single object, not a list
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"



# ════════════════════════════════════════════════════════════
#  TABLE 2 (NEW — Week 3): user_profiles
#
#  Why a separate table instead of adding columns to users?
#    - Keeps the users table focused on authentication only.
#    - Profile fields are optional; most can be NULL at first.
#    - Easy to extend later without touching the auth table.
#
#  One row = extra personal info for one registered user.
#  The row is created lazily — on first profile save/update.
# ════════════════════════════════════════════════════════════
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id      = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Links to users.id.  UNIQUE enforces one-to-one at DB level.
    # CASCADE: if user is deleted, profile is deleted automatically.
    user_id = Column(
                Integer,
                ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
                unique=True,
                index=True,
              )

    # ── Profile fields (all optional) ────────────────────────
    full_name  = Column(String(200), nullable=True)   # display / real name
    bio        = Column(Text,        nullable=True)   # short personal bio
    avatar_url = Column(String(500), nullable=True)   # URL to profile picture

    # ── Timestamps ───────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
                   DateTime(timezone=True),
                   server_default=func.now(),
                   onupdate=func.now(),   # refreshed automatically on every save
                 )

    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile user_id={self.user_id} full_name={self.full_name!r}>"




















 
# ════════════════════════════════════════════════════════════
#  TABLE 3: scan_history  (updated Week 3)
#  One row = one completed scan (URL or phone number).
#
#  Week 3 additions:
#    + risk_score  float 0.0–1.0 from the ML model
#    + notes       free-text explanation / AI reasoning
# ════════════════════════════════════════════════════════════
class ScanHistory(Base):
    __tablename__ = "scan_history"

    # ── Week 1 ───────────────────────────────────────────────
    id      = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
                Integer,
                ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,    # NULL = anonymous scan
                index=True,
              )
    result  = Column(Enum(ScanResult), nullable=False)

    # ── Week 2 ───────────────────────────────────────────────
    type        = Column(Enum(ScanType), nullable=False)
    input_value = Column(Text, nullable=False)
    timestamp   = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # ── Week 3 ───────────────────────────────────────────────
    # Confidence score from the detection model: 0.0 (safe) → 1.0 (phishing).
    # NULL when the model does not return a numeric score.
    #risk_score = Column(Float, nullable=True)

    # Explanation text — e.g. "Domain registered 2 days ago; no HTTPS."
    # Set by the ML pipeline; NULL if not available.
    #notes      = Column(Text, nullable=True)

    user = relationship("User", back_populates="scans")

    def __repr__(self):
        return (
            f"<ScanHistory id={self.id} "
            f"type={self.type} result={self.result} "
            f"risk={self.risk_score} input={str(self.input_value)[:30]!r}>"
        )