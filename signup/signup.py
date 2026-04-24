from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from signup.models import SignupRequest
from signup.hashpass import hash_password
from signup.validation import validate_password
from signup.email_security import is_disposable
from signup.email_verification import generate_verification_token, send_verification_email
from signup.user_validation import validate_username
from database import get_db
from crud import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    update_verification_token
)

router = APIRouter()

@router.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    email = request.email.strip().lower()
    username = request.username.strip()

    if is_disposable(email):
        raise HTTPException(status_code=400, detail="Disposable emails are not allowed")

    validate_username(username)
    validate_password(request.password)

    existing_email = get_user_by_email(db, email)

    if existing_email:
        if existing_email.is_verified:
            raise HTTPException(status_code=400, detail="Email already exists")

        token, expiry = generate_verification_token()

        try:
            update_verification_token(db, existing_email, token, expiry)
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500,
                detail="Database error while updating verification token"
            )

        send_verification_email(email, token)

        return {
            "message": "Account already exists but is not verified. Verification email resent."
        }

    existing_username = get_user_by_username(db, username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = hash_password(request.password)
    token, expiry = generate_verification_token()

    try:
        user = create_user(
            db=db,
            username=username,
            email=email,
            password_hash=hashed_pw,
            is_verified=False,
            verification_token=token,
            token_expiry=expiry
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error while creating user"
        )

    send_verification_email(email, token)

    return {
        "message": "User created successfully. Please check your email to verify your account."
    }