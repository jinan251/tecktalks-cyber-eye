from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.db_models import User
from backend.crud import get_user_by_email
from backend.login.auth import create_access_token   

router = APIRouter()


@router.post("/verify-email")
def verify_email(request: dict, db: Session = Depends(get_db)):

    # =========================
    # Get data from frontend
    # =========================
    email = request.get("email", "").strip().lower()
    code = str(request.get("otp_code", "")).strip()

    # =========================
    # Find user in database
    # =========================
    user = get_user_by_email(db, email)

    print("DB OTP:", user.verification_token)
    print("INPUT OTP:", code)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # =========================
    # Check OTP
    # =========================
    if str(user.verification_token).strip() != code:
        raise HTTPException(
            status_code=400,
            detail="Incorrect verification code. Please check your email and try again."
        )

    # =========================
    # Verify user
    # =========================
    user.is_verified = True
    user.verification_token = None
    user.token_expiry = None

    db.commit()

    # Create token after verification
    access_token = create_access_token({"user_id": user.id})

    return {
        "message": "verified_successfully",
        "access_token": access_token
    }