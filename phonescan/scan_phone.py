from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from crud import save_scan
from db_models import ScanType, ScanResult, User

from login.auth import get_current_user

from phonescan.models import PhoneRequest
from phonescan.phone_utils import normalize_phone, basic_format_check
from phonescan.phone_detection import detect_phone_local
from phonescan.phone_validation import validate_phone
from phonescan.phone_api import get_phone_info
from phonescan.phone_api_detection import analyze_phone_result

router = APIRouter()


def convert_status_to_scan_result(status: str) -> ScanResult:
    if status == "safe":
        return ScanResult.safe
    if status == "suspicious":
        return ScanResult.suspicious
    if status == "phishing":
        return ScanResult.phishing
    return ScanResult.unknown


@router.post("/scan-phone")
def scan_phone(
    request: PhoneRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # =========================
    # 1. INPUT VALIDATION
    # =========================
    if not request.phone:
        raise HTTPException(status_code=400, detail="Phone field is empty")

    phone = normalize_phone(request.phone)

    if not phone:
        raise HTTPException(status_code=400, detail="Invalid phone format")

    # =========================
    # 2. ANALYSIS LAYERS
    # =========================
    format_ok = basic_format_check(phone)
    validation_result = validate_phone(phone)

    local_result = detect_phone_local(phone)
    api_data = get_phone_info(phone)
    api_result = analyze_phone_result(api_data)

    local_status = local_result.get("status", "unknown")
    api_status = api_result.get("status", "unknown")

    # =========================
    # 3. FINAL DECISION (CLEAN LOGIC)
    # =========================

    if not format_ok or not validation_result.get("valid", False):
        final_status = "invalid"

    elif api_status == "phishing" or local_status == "phishing":
        final_status = "phishing"

    elif api_status == "suspicious" or local_status == "suspicious":
        final_status = "suspicious"

    elif api_status == "safe" and local_status == "safe":
        final_status = "safe"

    else:
        final_status = "unknown"

    # =========================
    # 4. SAVE
    # =========================
    save_scan(
        db=db,
        scan_type=ScanType.phone,
        input_value=phone,
        result=convert_status_to_scan_result(final_status),
        user_id=current_user.id
    )

    return {
        "phone": phone,
        "final_status": final_status,
        "validation": validation_result,
        "local_analysis": local_result,
        "api_analysis": api_result,
        "user_id": current_user.id,
        "saved": True
    }