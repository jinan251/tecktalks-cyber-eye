from fastapi import FastAPI
from phonescan.scan_phone import router as phone_router
from signup.signup import router as signup_router

app = FastAPI()

app.include_router(phone_router)
app.include_router(signup_router)
