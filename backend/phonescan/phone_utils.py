import re
import phonenumbers
from phonenumbers import NumberParseException, geocoder


def clean_phone(phone: str) -> str:
    
    phone = re.sub(r"[^\d+]", "", phone)
    return phone.strip()


def build_full_phone(phone: str, country_code: str):

    phone = clean_phone(phone)

    if phone.startswith("+"):
        return phone

    country_code = country_code.replace("+", "").strip()

    if phone.startswith("0"):
        phone = phone[1:]

    return f"+{country_code}{phone}"


def normalize_phone(phone: str, default_region="US"):
    try:
        parsed = phonenumbers.parse(phone, default_region)

        if not phonenumbers.is_possible_number(parsed):
            return None

        if not phonenumbers.is_valid_number(parsed):
            return None

        return phonenumbers.format_number(
            parsed,
            phonenumbers.PhoneNumberFormat.E164
        )

    except NumberParseException:
        return None


def basic_format_check(phone: str) -> bool:
    if not phone:
        return False

    if not phone.startswith("+"):
        return False

    digits = phone.replace("+", "")
    return digits.isdigit() and 7 <= len(digits) <= 15


def get_country(phone: str):
    try:
        parsed_number = phonenumbers.parse(phone, None)
        country = geocoder.description_for_number(parsed_number, "en")
        return country if country else "Unknown Country"
    except:
        return "Invalid Number"