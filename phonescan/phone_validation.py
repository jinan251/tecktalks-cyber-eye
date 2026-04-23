import phonenumbers
from phonenumbers import NumberParseException, geocoder, carrier

def validate_phone(phone: str):
    try:
        parsed = phonenumbers.parse(phone, None)

        is_valid = phonenumbers.is_valid_number(parsed)
        is_possible = phonenumbers.is_possible_number(parsed)

        return {
            "valid": is_valid,
            "possible": is_possible,
            "country_code": parsed.country_code,
            "region": geocoder.description_for_number(parsed, "en"),
            "carrier": carrier.name_for_number(parsed, "en")
        }

    except NumberParseException:
        return {
            "valid": False,
            "possible": False,
            "error": "Parsing failed"
        }