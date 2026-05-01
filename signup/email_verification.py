import os
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

def generate_verification_otp():
    """
    Generates a 6-digit numeric OTP and sets an expiration time of 1 hour.
    """
    # Generate a random 6-digit number as a string
    otp_code = f"{random.randint(100000, 999999)}"
    # Set expiration time to 1 hour from now
    expiry = datetime.utcnow() + timedelta(hours=1)
    return otp_code, expiry


def send_verification_email(email: str, otp_code: str):
    """
    Sends an email to the user containing the 6-digit verification code.
    No links are included as per the new UI requirements.
    """
    msg = EmailMessage()
    msg["Subject"] = "Your CyberEye Verification Code"
    msg["From"] = EMAIL_USER
    msg["To"] = email

    # Email body updated to show only the numeric code
    msg.set_content(f"""
Hello,

Thank you for signing up to CyberEye.

Your verification code is: {otp_code}

This code will expire in 1 hour. 

Please enter this code in the application to verify your account.

If you did not create this account, you can ignore this email.
""")

    # Debugging logs to verify credentials
    print("EMAIL_USER:", EMAIL_USER)
    print("PASSWORD EXISTS:", EMAIL_APP_PASSWORD is not None)

    try:
        # Connect to Gmail SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_APP_PASSWORD)
            smtp.send_message(msg)
            print(f"OTP sent successfully to {email}")
    except Exception as e:
        print("Email sending error:", e)
        raise