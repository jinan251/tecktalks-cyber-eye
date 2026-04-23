from pydantic import BaseModel, EmailStr

# ✅ Login request
class LoginRequest(BaseModel):
    email: EmailStr
    password: str