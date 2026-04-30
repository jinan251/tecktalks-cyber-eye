import random
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


# Import your local modules
from signup.models import SignupRequest
from signup.hashpass import hash_password
from signup.validation import validate_password
from signup.email_security import is_disposable
from signup.email_verification import send_verification_email
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
    """
    Handles user registration, generates a 6-digit OTP,
    and ensures it is saved to the database.
    """
    email = request.email.strip().lower()
    username = request.username.strip()

    # 1. Security & Validation Checks
    if is_disposable(email):
        raise HTTPException(status_code=400, detail="Disposable emails are not allowed")

    validate_username(username)
    validate_password(request.password)

    # 2. Check if the email is already in the system
    existing_email = get_user_by_email(db, email)

    if existing_email:
        # If the user is already verified, don't allow duplicate registration
        if existing_email.is_verified:
            raise HTTPException(status_code=400, detail="Email already exists and is verified.")

        # If not verified, generate a NEW 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        expiry = 3600 # 1 hour

        try:
            # Force update the token in the database
            existing_email.verification_token = otp_code
            db.add(existing_email)
            db.commit() # CRITICAL: Ensure the token is saved to avoid 'DB:[]' error
           
            # Send the numeric code to the user's email
            send_verification_email(email, otp_code)
            return {"message": "Account exists but not verified. New code sent to your email."}
       
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error updating token: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error while updating token")

    # 3. Check if username is taken
    existing_username = get_user_by_username(db, username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    # 4. Create a new user with an unverified status
    hashed_pw = hash_password(request.password)
    otp_code = str(random.randint(100000, 999999))
    expiry = 3600

    try:
        new_user = create_user(
            db=db,
            username=username,
            email=email,
            password_hash=hashed_pw,
            is_verified=False,
            verification_token=otp_code,
            token_expiry=expiry
        )
        db.commit() # CRITICAL: Ensure the new user is saved immediately
       
        # Send the code
        send_verification_email(email, otp_code)
       
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while creating user")

    return {
        "message": "User created successfully. Please enter the 6-digit code sent to your email."
    }

