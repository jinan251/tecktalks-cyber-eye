# crud.py

from sqlalchemy.orm import Session
from db_models import User, ScanHistory, ScanType, ScanResult
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

def get_scan_history(
    db: Session,
    user_id: int | None = None,
    scan_type: ScanType | None = None,
    limit: int = 20,
) -> list[ScanHistory]:
    query = db.query(ScanHistory).order_by(ScanHistory.timestamp.desc())
    if user_id is not None:
        query = query.filter(ScanHistory.user_id == user_id)
    if scan_type is not None:
        query = query.filter(ScanHistory.type == scan_type)
    return query.limit(limit).all()

def get_scan_by_id(db: Session, scan_id: int) -> ScanHistory | None:
    return db.query(ScanHistory).filter(ScanHistory.id == scan_id).first()