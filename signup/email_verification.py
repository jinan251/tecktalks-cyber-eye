import os
import secrets
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
FRONTEND_VERIFY_URL = os.getenv(
    "FRONTEND_VERIFY_URL",
    "http://127.0.0.1:8000/verify-email"
)

def generate_verification_token():
    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(hours=1)
    return token, expiry


def send_verification_email(email: str, token: str):
    verification_link = f"{FRONTEND_VERIFY_URL}?token={token}"

    msg = EmailMessage()
    msg["Subject"] = "Verify your CyberEye account"
    msg["From"] = EMAIL_USER
    msg["To"] = email

    msg.set_content(f"""
Hello,

Thank you for signing up to CyberEye.

Please verify your email by clicking this link:

{verification_link}

This link will expire in 1 hour.

If you did not create this account, you can ignore this email.
""")
    print("EMAIL_USER:", EMAIL_USER)
    print("PASSWORD EXISTS:", EMAIL_APP_PASSWORD is not None)
    print("PASSWORD LENGTH:", len(EMAIL_APP_PASSWORD) if EMAIL_APP_PASSWORD else 0)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_APP_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print("Email sending error:", e)
        raise