import re

def detect_phone_local(phone: str):
    score = 0
    reasons = []

    digits = phone.replace("+", "")

    # Too short / too long
    if len(digits) < 7:
        score += 5
        reasons.append("Too short")

    if len(digits) > 15:
        score += 5
        reasons.append("Too long")

    # Repeated digits
    if re.fullmatch(r"(\d)\1{6,}", digits):
        score += 5
        reasons.append("Repeated same digit")

    # Sequential patterns
    sequences = ["123456", "234567", "345678", "456789", "000000", "111111", "999999"]
    if any(seq in digits for seq in sequences):
        score += 3
        reasons.append("Sequential pattern")

    # Too many zeros
    if digits.count("0") >= len(digits) // 2 and len(digits) >= 8:
        score += 2
        reasons.append("Too many zeros")

    # Invalid characters (safety)
    if not re.fullmatch(r"\+?\d+", phone):
        score += 4
        reasons.append("Invalid characters")

    # Final decision
    if score >= 7:
        status = "suspicious"
    elif score >= 4:
        status = "unknown"
    else:
        status = "safe"

    return {
        "status": status,
        "score": score,
        "reasons": reasons
    }