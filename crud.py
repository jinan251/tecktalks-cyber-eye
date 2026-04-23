# ============================================================
#  crud.py
#  CyberEye — Weeks 1 & 2
#
#  What this file does:
#    Contains every database operation the backend needs.
#    CRUD = Create, Read, Update, Delete.
#    The backend team imports functions from here — they never
#    write raw SQL or touch the database directly.
#
#  Imports from:
#    ← database.py   (SessionLocal)
#    ← db_models.py  (User, ScanHistory, ScanType, ScanResult)
#
#  Who uses it:
#    → main.py  calls  save_scan, create_user, get_user_by_email
# ============================================================

from sqlalchemy.orm import Session
from db_models import User, ScanHistory, ScanType, ScanResult


# ════════════════════════════════════════════════════════════
#  USER OPERATIONS
#  Added in Week 2 — needed for login and sign-up system.
# ════════════════════════════════════════════════════════════

def create_user(db: Session, username: str, email: str, password_hash: str) -> User:
    """
    [Week 2] Inserts a new user into the users table.

    ⚠️  password_hash must already be hashed BEFORE calling this.
        The backend does:  hash = bcrypt.hashpw(password, bcrypt.gensalt())
        Then passes the hash here — never the plain password.

    Called by:  POST /signup  endpoint in main.py
    Raises:     IntegrityError if username or email already exists.
    """
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
    )
    db.add(user)
    db.commit()
    db.refresh(user)   # reloads the row so 'id' and 'created_at' are filled in
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    [Week 2] Finds a user by their email address.

    Called by:  POST /login  to check if the email exists,
                then backend compares the password hash.
    Returns:    User object if found, None if not found.
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """
    [Week 2] Finds a user by their username.

    Called by:  POST /signup  to check if the username is already taken
                before creating the account.
    Returns:    User object if found, None if not found.
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    [Week 2] Finds a user by their ID number.

    Useful when a logged-in user's ID is stored in a session token
    and you need to fetch their full profile.
    """
    return db.query(User).filter(User.id == user_id).first()


# ════════════════════════════════════════════════════════════
#  SCAN HISTORY OPERATIONS
#  save_scan existed in Week 1. Everything else added in Week 2.
# ════════════════════════════════════════════════════════════

def save_scan(
    db: Session,
    scan_type: ScanType,          # ScanType.url  or  ScanType.phone
    input_value: str,             # the actual URL or phone number
    result: ScanResult,           # ScanResult.safe / .suspicious / .phishing / .unknown
    user_id: int | None = None,   # None = anonymous (not logged in)
) -> ScanHistory:
    """
    [Week 1 + Week 2] Saves a completed scan to scan_history.

    Week 1: was called with url + result only (URL scans only).
    Week 2: now accepts scan_type + input_value to support phone scans too.

    Usage examples:
        # URL scan (logged-in user)
        save_scan(db, ScanType.url, "http://evil.com", ScanResult.phishing, user_id=3)

        # Phone scan (anonymous)
        save_scan(db, ScanType.phone, "+1-900-555-0199", ScanResult.suspicious)

    Called by:  POST /scan-link   (URL scan endpoint)
                POST /scan-phone  (phone scan endpoint — Week 2)
    """
    scan = ScanHistory(
        user_id=user_id,
        type=scan_type,
        input_value=input_value,
        result=result,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def get_scan_history(
    db: Session,
    user_id: int | None = None,
    scan_type: ScanType | None = None,
    limit: int = 20,
) -> list[ScanHistory]:
    """
    [Week 1 + Week 2] Returns recent scans, newest first.

    Filters (all optional):
        user_id   → only return scans from this user
        scan_type → only return 'url' or 'phone' scans
        limit     → max number of rows to return (default 20)

    If no filters, returns all scans (admin/debug use).
    Called by:  future GET /history  endpoint.
    """
    query = db.query(ScanHistory).order_by(ScanHistory.timestamp.desc())

    if user_id is not None:
        query = query.filter(ScanHistory.user_id == user_id)

    if scan_type is not None:
        query = query.filter(ScanHistory.type == scan_type)

    return query.limit(limit).all()


def get_scan_by_id(db: Session, scan_id: int) -> ScanHistory | None:
    """
    [Week 2] Returns a single scan record by its ID.
    Useful for looking up one specific scan result.
    """
    return db.query(ScanHistory).filter(ScanHistory.id == scan_id).first()
