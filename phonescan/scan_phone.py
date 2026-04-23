from fastapi import APIRouter, HTTPException
from phonescan.models import PhoneRequest
from phonescan.phone_utils import normalize_phone,basic_format_check
from phonescan.phone_detection import detect_phone_local
from phonescan.phone_validation import validate_phone
from phonescan.phone_api import get_phone_info
from phonescan.phone_api_detection import analyze_phone_result
router = APIRouter()

@router.post("/scan-phone")
def scan_phone(request: PhoneRequest):
    phone = normalize_phone(request.phone)

    if not phone:
        raise HTTPException(status_code=400, detail="Phone is required")

    # 1. validation
    format_ok = basic_format_check(phone)
    validation_result = validate_phone(phone)

    # 2. local detection
    local_result = detect_phone_local(phone)

    # 3. API result
    api_data = get_phone_info(phone)
    api_result = analyze_phone_result(api_data)

    local_status = local_result["status"]
    api_status = api_result["status"]

    # 4. final decision
    if not format_ok or not validation_result.get("valid", False):
        final_status = "invalid"

    elif local_status == "suspicious" or api_status == "suspicious":
        final_status = "suspicious"

    elif local_status == "safe" and validation_result.get("valid", False):
        final_status = "safe"

    else:
        final_status = "unknown"

    return {
        "phone": phone,
        "final_status": final_status,
        "validation": validation_result,
        "local_analysis": local_result,
        "api_analysis": api_result
    }