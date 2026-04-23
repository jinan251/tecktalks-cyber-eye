from fastapi import APIRouter, HTTPException
from database import SessionLocal
from db_models import User
from models import LoginRequest
from hash import verify_password
from auth import create_access_token

router = APIRouter()

@router.post("/login")
def login(request: LoginRequest):
    db = SessionLocal()

    try:
        # normalize email
        email = request.email.strip().lower()

        # find user by email
        user = db.query(User).filter(User.email == email).first()

        # generic error message for security
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # verify password
        if not verify_password(request.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # create JWT token
        access_token = create_access_token({
            "user_id": user.id,
            "email": user.email
        })

        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer"
        }

    finally:
        db.close()