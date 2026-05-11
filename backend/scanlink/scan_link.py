from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.crud import save_scan
from backend.db_models import ScanType, ScanResult, User

from backend.login.auth import get_current_user   # 🔐 JWT

from backend.scanlink.models import URLRequest
from backend.scanlink.detection import detect_link
from backend.scanlink.google_safe import check_google_safe
from backend.scanlink.virustotal import check_virustotal

router = APIRouter()


def convert_to_enum(result: str) -> ScanResult:
    if result == "safe":
        return ScanResult.safe
    if result == "suspicious":
        return ScanResult.suspicious
    if result == "phishing":
        return ScanResult.phishing
    return ScanResult.unknown


@router.post("/scan-link")
def scan_link(

    
    request: URLRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)   # 🔐 PROTECTED
    
):
    url = request.url.strip()

    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    # 1. Heuristic detection
    heuristic_result = detect_link(url)

    # 2. Google Safe Browsing
    google_result = check_google_safe(url)

    # 3. VirusTotal detection
    vt_result = check_virustotal(url)

    # 4. Final decision
    if google_result == "phishing" or vt_result == "phishing":
        final_result = "phishing"

    elif vt_result == "suspicious":
        final_result = "suspicious"

    elif heuristic_result == "phishing":
        final_result = "phishing"

    elif heuristic_result == "suspicious":
        final_result = "suspicious"

    else:
        final_result = "safe"

    # 5. Save in DB WITH USER
    save_scan(
        db=db,
        scan_type=ScanType.url,
        input_value=url,
        result=convert_to_enum(final_result),
        user_id=current_user.id   # 🔥 NOW LINKED TO USER
    )

    return {
    "url": url,
    "final_result": final_result,
    "details": {
        "heuristic": heuristic_result,
        "google": google_result
    },
    "saved": True
}