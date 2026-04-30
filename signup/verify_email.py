from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from db_models import User
# IMPORT the token creation function (Verify the path to your security/auth file)
# from login.auth import create_access_token 

router = APIRouter()

class VerifyRequest(BaseModel):
    email: str
    otp_code: str

@router.post("/verify-email")
def verify_email(request: VerifyRequest, db: Session = Depends(get_db)):

    #Verifies the user's email and returns a JWT token so the frontend can log in immediately.
    
    user = db.query(User).filter(User.email == request.email.strip().lower()).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stored_otp = str(user.verification_token).strip()
    input_otp = str(request.otp_code).strip()

    if stored_otp != input_otp:
        raise HTTPException(status_code=400, detail="Invalid or Expired OTP.")

    # Update user status
    user.is_verified = True
    user.verification_token = None 
    user.token_expiry = None

    try:
        db.commit()
        
        # --- CRITICAL FIX START ---
        # We need to return an access_token here so Gradio can store it in 'auth_token'
        # If you don't have a create_access_token function yet, you can return a simple success status
        # but the scanner needs a token. For now, we mimic the login response structure.
        
        from login.auth import create_access_token

        access_token = create_access_token(
        data={"user_id": user.id}
        )
        
        return {
            "message": "Email verified successfully!",
            "access_token": access_token, # This matches what Gradio expects
            "token_type": "bearer"
        }
        # --- CRITICAL FIX END ---

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
