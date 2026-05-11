from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.login.auth import get_current_user
from backend.db_models import User, ScanType, ScanResult
from backend.crud import get_scan_history, count_scan_history, delete_scan

router = APIRouter()


@router.get("/history")
def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    scan_type: ScanType | None = Query(None),
    result: ScanResult | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    offset = (page - 1) * limit

    total = count_scan_history(
        db=db,
        user_id=current_user.id,
        scan_type=scan_type,
        result_filter=result
    )

    history = get_scan_history(
        db=db,
        user_id=current_user.id,
        scan_type=scan_type,
        result_filter=result,
        limit=limit,
        offset=offset
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit,
        "history": [
            {
                "id": scan.id,
                "type": scan.type.value if hasattr(scan.type, "value") else scan.type,
                "input_value": scan.input_value,
                "result": scan.result.value if hasattr(scan.result, "value") else scan.result,
                "timestamp": scan.timestamp
            }
            for scan in history
        ]
    }


@router.delete("/history/{scan_id}")
def delete_history_item(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted = delete_scan(
        db=db,
        scan_id=scan_id,
        user_id=current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Scan not found"
        )

    return {
        "message": "History item deleted successfully",
        "deleted_id": scan_id
    }