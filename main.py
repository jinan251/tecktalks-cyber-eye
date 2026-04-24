from fastapi import FastAPI
from phonescan.scan_phone import router as phone_router
from signup.signup import router as signup_router
from database import init_db
from signup.verify_email import router as verify_email_router
from login.login import router as login_router
from scanlink.scan_link import router as link_router
app = FastAPI()
init_db()
app.include_router(phone_router)
app.include_router(signup_router)
app.include_router(verify_email_router)
app.include_router(login_router)
app.include_router(link_router)