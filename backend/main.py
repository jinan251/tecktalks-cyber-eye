from fastapi import FastAPI
from backend.phonescan.scan_phone import router as phone_router
from backend.signup.signup import router as signup_router
from backend.database import init_db
from backend.signup.verify_email import router as verify_email_router
from backend.login.login import router as login_router
from backend.scanlink.scan_link import router as link_router
from backend.history import router as history_router
from backend.profile import router as profile_router
from backend.phonescan.countries import router as countries_router
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
init_db()
app.include_router(phone_router)
app.include_router(signup_router)
app.include_router(verify_email_router)
app.include_router(login_router)
app.include_router(link_router)
app.include_router(history_router)
app.include_router(profile_router)
app.include_router(countries_router)