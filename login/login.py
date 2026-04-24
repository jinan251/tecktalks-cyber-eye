from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from crud import get_user_by_email

from login.models import LoginRequest
from login.hash import verify_password
from login.auth import create_access_token

router = APIRouter()

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    email = request.email.strip().lower()

    user = get_user_by_email(db, email)

    # Generic error (good for security)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email first")

    # 🔐 Create JWT token safely
    try:
        access_token = create_access_token({
            "user_id": user.id,
            "email": user.email
        })
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error generating token"
        )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }