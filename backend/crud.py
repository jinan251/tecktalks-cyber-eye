# crud.py

from sqlalchemy.orm import Session
from backend.db_models import User,UserProfile ,ScanHistory, ScanType, ScanResult
from sqlalchemy.exc import SQLAlchemyError

# ════════════════════════════════════════════════════════════
#  USER OPERATIONS
# ════════════════════════════════════════════════════════════

def create_user(db: Session, username: str, email: str, password_hash: str,
                is_verified=False, verification_token=None, token_expiry=None):
    """
    Inserts a new user with OTP verification support.
    """
    try:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            is_verified=is_verified,
            verification_token=verification_token,
            token_expiry=token_expiry
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    except SQLAlchemyError:
        db.rollback()
        raise

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def update_verification_token(db: Session, user: User, token: str, expiry: int):
    """
    Updates the OTP token for an existing user.
    """
    try:
        user.verification_token = token
        user.token_expiry = expiry
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError:
        db.rollback()
        raise

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
#  SCAN HISTORY OPERATIONS
# ════════════════════════════════════════════════════════════

def save_scan(
    db: Session,
    scan_type: ScanType,
    input_value: str,
    result: ScanResult,
    user_id: int | None = None,
) -> ScanHistory:
    try:
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
    except SQLAlchemyError:
        db.rollback()
        raise

#def get_scan_history(
    #db: Session,
    #user_id: int | None = None,
    #scan_type: ScanType | None = None,
    #limit: int = 20,
#) -> list[ScanHistory]:
    #query = db.query(ScanHistory).order_by(ScanHistory.timestamp.desc())
    #if user_id is not None:
       # query = query.filter(ScanHistory.user_id == user_id)
   # if scan_type is not None:
       # query = query.filter(ScanHistory.type == scan_type)
   # return query.limit(limit).all()

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


#def get_scan_by_id(db: Session, scan_id: int) -> ScanHistory | None:
   # return db.query(ScanHistory).filter(ScanHistory.id == scan_id).first()




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