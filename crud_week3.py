# ============================================================
#  crud.py
#  CyberEye — Weeks 1, 2 & 3
#
#  What this file does:
#    Contains every database operation the backend needs.
#    CRUD = Create, Read, Update, Delete.
#    The backend team imports functions from here — they never
#    write raw SQL or touch the database directly.
#
#  Imports from:
#    ← database.py   (SessionLocal)
#    ← db_models.py  (User, UserProfile, ScanHistory, ScanType, ScanResult)
#
#  Who uses it:
#    → main.py  calls any function from here
#
#  Week 3 additions:
#    - create_or_update_profile()
#    - get_profile()
#    - get_user_with_profile()
#    - save_scan() updated: accepts risk_score + notes
#    - get_scan_history() updated: added scan_type filter + total_count helper
#    - delete_scan()  (new — lets users remove a scan from their history)
# ============================================================

from sqlalchemy.orm import Session
from db_models import User, UserProfile, ScanHistory, ScanType, ScanResult


# ════════════════════════════════════════════════════════════
#  USER OPERATIONS  (Week 2 — unchanged)
# ════════════════════════════════════════════════════════════

def create_user(db: Session, username: str, email: str, password_hash: str) -> User:
    """
    [Week 2] Inserts a new user into the users table.

    ⚠️  password_hash must be hashed BEFORE calling this.
    Raises IntegrityError if username or email already exists.
    Called by: POST /signup
    """
    user = User(username=username, email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """[Week 2] Find user by email. Used in POST /login."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """[Week 2] Find user by username. Used in POST /signup to check availability."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """[Week 2] Find user by ID. Used when reading from a session/JWT token."""
    return db.query(User).filter(User.id == user_id).first()


# ════════════════════════════════════════════════════════════
#  PROFILE OPERATIONS  (NEW — Week 3)
# ════════════════════════════════════════════════════════════

def get_profile(db: Session, user_id: int) -> UserProfile | None:
    """
    [Week 3] Returns the UserProfile row for the given user_id.

    Returns None if the user hasn't set up a profile yet.
    Called by: GET /profile
    """
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()


def create_or_update_profile(
    db: Session,
    user_id: int,
    full_name: str | None = None,
    bio: str | None = None,
    avatar_url: str | None = None,
) -> UserProfile:
    """
    [Week 3] Creates a profile if none exists, otherwise updates it.

    This is an "upsert" — safe to call whether or not a profile row
    already exists for this user.

    Only fields that are explicitly passed (not None) are updated,
    so partial updates work without overwriting existing data.

    Usage:
        # First time (creates row)
        create_or_update_profile(db, user_id=3, full_name="Sara")

        # Update just the bio later
        create_or_update_profile(db, user_id=3, bio="Security researcher")

    Called by: PUT /profile  or  PATCH /profile
    """
    profile = get_profile(db, user_id)

    if profile is None:
        # No profile yet — create a fresh one
        profile = UserProfile(
            user_id=user_id,
            full_name=full_name,
            bio=bio,
            avatar_url=avatar_url,
        )
        db.add(profile)
    else:
        # Profile exists — only overwrite fields that were provided
        if full_name is not None:
            profile.full_name = full_name
        if bio is not None:
            profile.bio = bio
        if avatar_url is not None:
            profile.avatar_url = avatar_url

    db.commit()
    db.refresh(profile)
    return profile


def get_user_with_profile(db: Session, user_id: int) -> User | None:
    """
    [Week 3] Returns the User object with the profile already loaded.

    SQLAlchemy will join user_profiles automatically because of the
    relationship defined in db_models.py.

    After calling this:
        user.profile.full_name  →  "Sara"
        user.profile.bio        →  "Security researcher"
        user.profile            →  None  (if profile not created yet)

    Called by: GET /me  (returns combined user + profile data)
    """
    return db.query(User).filter(User.id == user_id).first()


# ════════════════════════════════════════════════════════════
#  SCAN HISTORY OPERATIONS  (updated Week 3)
# ════════════════════════════════════════════════════════════

def save_scan(
    db: Session,
    scan_type: ScanType,
    input_value: str,
    result: ScanResult,
    user_id: int | None = None,
    risk_score: float | None = None,   # Week 3: 0.0–1.0 from model
    notes: str | None = None,          # Week 3: explanation text
) -> ScanHistory:
    """
    [Week 1 + Week 2 + Week 3] Saves a completed scan to scan_history.

    Week 3 adds risk_score and notes so the ML pipeline can store
    its confidence value and a human-readable explanation alongside
    each result.

    Usage:
        save_scan(
            db,
            ScanType.url,
            "http://evil.com",
            ScanResult.phishing,
            user_id=3,
            risk_score=0.97,
            notes="Domain registered 2 days ago; no HTTPS.",
        )

    Called by: POST /scan-link, POST /scan-phone
    """
    scan = ScanHistory(
        user_id=user_id,
        type=scan_type,
        input_value=input_value,
        result=result,
        risk_score=risk_score,
        notes=notes,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def get_scan_history(
    db: Session,
    user_id: int | None = None,
    scan_type: ScanType | None = None,
    result_filter: ScanResult | None = None,   # Week 3: filter by verdict
    limit: int = 20,
    offset: int = 0,                           # Week 3: pagination support
) -> list[ScanHistory]:
    """
    [Week 1 + Week 2 + Week 3] Returns recent scans, newest first.

    Filters (all optional):
        user_id       → only scans from this user
        scan_type     → only 'url' or 'phone' scans
        result_filter → only scans with this verdict (e.g. ScanResult.phishing)
        limit         → max rows to return (default 20)
        offset        → skip this many rows — use for pagination

    Example (page 2, 20 results per page):
        get_scan_history(db, user_id=3, limit=20, offset=20)

    Called by: GET /history
    """
    query = db.query(ScanHistory).order_by(ScanHistory.timestamp.desc())

    if user_id is not None:
        query = query.filter(ScanHistory.user_id == user_id)
    if scan_type is not None:
        query = query.filter(ScanHistory.type == scan_type)
    if result_filter is not None:
        query = query.filter(ScanHistory.result == result_filter)

    return query.offset(offset).limit(limit).all()


def count_scan_history(
    db: Session,
    user_id: int | None = None,
    scan_type: ScanType | None = None,
    result_filter: ScanResult | None = None,
) -> int:
    """
    [Week 3] Returns the total number of scans matching the filters.

    Use alongside get_scan_history() to build paginated responses:

        total  = count_scan_history(db, user_id=3)
        scans  = get_scan_history(db, user_id=3, limit=20, offset=0)
        # → { "total": total, "items": scans }

    Called by: GET /history  (to populate pagination metadata)
    """
    query = db.query(ScanHistory)

    if user_id is not None:
        query = query.filter(ScanHistory.user_id == user_id)
    if scan_type is not None:
        query = query.filter(ScanHistory.type == scan_type)
    if result_filter is not None:
        query = query.filter(ScanHistory.result == result_filter)

    return query.count()


def get_scan_by_id(db: Session, scan_id: int) -> ScanHistory | None:
    """[Week 2] Returns a single scan by its ID."""
    return db.query(ScanHistory).filter(ScanHistory.id == scan_id).first()


def delete_scan(db: Session, scan_id: int, user_id: int) -> bool:
    """
    [Week 3] Deletes one scan from history.

    user_id is required as a safety check — a user can only delete
    their own scans, not someone else's.

    Returns True if the scan was found and deleted, False if not found
    or if the scan belongs to a different user.

    Called by: DELETE /history/{scan_id}
    """
    scan = (
        db.query(ScanHistory)
        .filter(ScanHistory.id == scan_id, ScanHistory.user_id == user_id)
        .first()
    )
    if scan is None:
        return False

    db.delete(scan)
    db.commit()
    return True
