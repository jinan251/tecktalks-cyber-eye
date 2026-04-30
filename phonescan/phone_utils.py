import phonenumbers
from phonenumbers import NumberParseException

def normalize_phone(phone: str, default_region="US"):
    """
    Normalize phone number to E.164 format (GLOBAL)
    """
    if not phone:
        return None

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
    """
    Basic validation after normalization
    """
    if not phone:
        return False

    # must start with +
    if not phone.startswith("+"):
        return False

    # length check (E.164 max 15 digits)
    digits = phone.replace("+", "")
    if not digits.isdigit() or not (7 <= len(digits) <= 15):
        return False

    return True