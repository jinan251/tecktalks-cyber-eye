from fastapi import APIRouter, HTTPException
from signup.models import SignupRequest
from signup.hashpass import hash_password
from signup.validation import validate_password
from signup.email_security import is_disposable

router = APIRouter()

@router.post("/signup")
def signup(request: SignupRequest):

    # ✅ normalize email
    email = request.email.strip().lower()

    # ❌ block disposable emails
    if is_disposable(email):
        raise HTTPException(400, "Disposable emails are not allowed")

    # username validation
    if len(request.username) < 3:
        raise HTTPException(400, "Username too short")

    # password validation
    validate_password(request.password)

    # 🔐 hash password
    hashed_pw = hash_password(request.password)

    # 🔥 TEMPORARY RESPONSE (no DB yet)
    return {
        "message": "Signup successful (no DB yet)",
        "username": request.username,
        "email": email,
        "hashed_password": hashed_pw   # for testing only
    }