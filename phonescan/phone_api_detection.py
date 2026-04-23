def analyze_phone_result(data: dict):
    if "error" in data:
        return {
            "status": "unknown",
            "message": "Phone lookup failed"
        }

    is_valid = data.get("valid")
    line_type = str(data.get("type", "")).lower()
    carrier = data.get("carrier", "")
    country = data.get("country", "")

    if is_valid is False:
        return {
            "status": "suspicious",
            "message": "Invalid phone number",
            "carrier": carrier,
            "country": country,
            "line_type": line_type
        }

    if "voip" in line_type:
        return {
            "status": "suspicious",
            "message": "VoIP number detected",
            "carrier": carrier,
            "country": country,
            "line_type": line_type
        }

    if is_valid is True:
        return {
            "status": "safe",
            "message": "Phone number looks valid",
            "carrier": carrier,
            "country": country,
            "line_type": line_type
        }

    return {
        "status": "unknown",
        "message": "Could not determine phone status",
        "carrier": carrier,
        "country": country,
        "line_type": line_type
    }