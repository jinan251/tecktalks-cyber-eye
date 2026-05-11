from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.crud import save_scan
from backend.db_models import ScanType, ScanResult, User

from backend.login.auth import get_current_user
from backend.phonescan.phone_utils import get_country
from backend.phonescan.models import PhoneRequest

from backend.phonescan.phone_utils import (
    normalize_phone,
    basic_format_check,
    build_full_phone
)

from backend.phonescan.phone_detection import detect_phone_local
from backend.phonescan.phone_validation import validate_phone
from backend.phonescan.phone_api import get_phone_info
from backend.phonescan.phone_api_detection import analyze_phone_result

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
    # INPUT VALIDATION
    # =========================
    if not request.phone:
        raise HTTPException(status_code=400, detail="Phone field is empty")

    if not request.country_code:
        raise HTTPException(status_code=400, detail="Please select a country code")

    # =========================
    # BUILD + NORMALIZE
    # =========================
    full_phone = build_full_phone(request.phone, request.country_code)
    phone = normalize_phone(full_phone)

    if not phone:
        raise HTTPException(status_code=400, detail="Invalid phone format")

    country = get_country(phone)

    # =========================
    # ANALYSIS
    # =========================
    validation_result = validate_phone(phone)
    local_result = detect_phone_local(phone)

    api_data = get_phone_info(phone) or {}
    api_result = analyze_phone_result(api_data)

    local_status = local_result.get("status", "unknown")
    api_status = api_result.get("status", "unknown")

    # =========================
    # SCORING SYSTEM
    # =========================
    score = 0

    if validation_result.get("valid"):
        score += 40

    if api_status == "safe":
        score += 35
    elif api_status == "suspicious":
        score += 15
    elif api_status == "phishing":
        score -= 20

    if local_status == "safe":
        score += 25
    elif local_status == "suspicious":
        score += 10
    elif local_status == "unknown":
        score += 5

    # =========================
    # FINAL DECISION
    # =========================
    if score >= 80:
        final_status = "safe"
    elif score >= 50:
        final_status = "suspicious"
    else:
        final_status = "phishing"

    # =========================
    # SAVE
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
        "country": country,
        "final_status": final_status,
        "saved": True
    }