# email_security.py

DISPOSABLE_DOMAINS = {
    "mailinator.com",
    "tempmail.com",
    "10minutemail.com",
    "guerrillamail.com",
    "trashmail.com",
    "yopmail.com"
}

def is_disposable(email: str) -> bool:
    domain = email.split("@")[-1]
    return domain in DISPOSABLE_DOMAINS