import re

def normalize_phone(phone: str) -> str:
    phone = phone.strip()
    phone = re.sub(r"[^\d+]", "", phone)
    return phone


def basic_format_check(phone: str) -> bool:
    return bool(re.fullmatch(r"\+?\d{7,15}", phone))