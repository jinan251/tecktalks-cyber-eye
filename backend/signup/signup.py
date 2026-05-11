import random
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.signup.models import SignupRequest
from backend.signup.validation import validate_password
from backend.signup.email_security import is_disposable
from backend.signup.email_verification import send_verification_email
from backend.signup.user_validation import validate_username
from backend.signup.hashpass import hash_password

from backend.database import get_db
from backend.crud import (
    get_user_by_email,
    get_user_by_username,
    create_user,
)

router = APIRouter()


@router.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):

    email = request.email.strip().lower()
    username = request.username.strip()

    # =========================
    # Validate username
    # =========================
    validate_username(username)

    # =========================
    # Validate password
    # =========================
    validate_password(request.password)

    # =========================
    # Disposable email check
    # =========================
    if is_disposable(email):
        raise HTTPException(
            status_code=400,
            detail="Disposable emails are not allowed"
        )

    # =========================
    # Generate OTP
    # =========================
    code = str(random.randint(100000, 999999))

    # =========================
    # Existing email?
    # =========================
    existing_user = get_user_by_email(db, email)

    if existing_user:

        # VERIFIED USER
        if existing_user.is_verified:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

        # NOT VERIFIED USER
        # Update data instead of creating new user
        existing_user.username = username
        existing_user.password_hash = hash_password(request.password)
        existing_user.verification_token = code

        db.commit()

        send_verification_email(email, code)

        return {
            "message": "verification_sent"
        }

    # =========================
    # Username already exists?
    # =========================
    username_exists = get_user_by_username(db, username)

    if username_exists and username_exists.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # =========================
    # Create new user
    # =========================
    hashed_password = hash_password(request.password)

    create_user(
        db=db,
        username=username,
        email=email,
        password_hash=hashed_password,
        is_verified=False,
        verification_token=code,
        token_expiry=None
    )

    # =========================
    # Send OTP
    # =========================
    send_verification_email(email, code)

    return {
        "message": "verification_sent"
    }