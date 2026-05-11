from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.orm import Session
import re

from backend.database import get_db
from backend.login.auth import get_current_user
from backend.db_models import User, ScanHistory, ScanResult
from backend.crud import get_profile, create_or_update_profile

router = APIRouter()


def is_image_url(url: str) -> bool:
    return re.search(r"\.(jpg|jpeg|png|gif|webp)$", url.lower()) is not None


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=100)
    bio: str | None = Field(None, max_length=300)
    avatar_url: HttpUrl | None = None


@router.get("/profile")
def read_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_profile(db, current_user.id)

    completion = 0
    if profile and profile.full_name:
        completion += 1
    if profile and profile.bio:
        completion += 1
    if profile and profile.avatar_url:
        completion += 1

    completion_percentage = int((completion / 3) * 100) if profile else 0

    total_scans = db.query(ScanHistory).filter(
        ScanHistory.user_id == current_user.id
    ).count()

    phishing_scans = db.query(ScanHistory).filter(
        ScanHistory.user_id == current_user.id,
        ScanHistory.result == ScanResult.phishing
    ).count()

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "profile": {
            "full_name": profile.full_name if profile else None,
            "bio": profile.bio if profile else None,
            "avatar_url": profile.avatar_url if profile else None,
            "updated_at": profile.updated_at if profile else None,
        },
        "profile_completion": completion_percentage,
        "stats": {
            "total_scans": total_scans,
            "phishing_found": phishing_scans
        }
    }


@router.patch("/profile")
def update_profile(
    request: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if (
        request.full_name is None
        and request.bio is None
        and request.avatar_url is None
    ):
        raise HTTPException(
            status_code=400,
            detail="No data provided to update"
        )

    avatar_url = None

    if request.avatar_url:
        avatar_url = str(request.avatar_url)

        if not is_image_url(avatar_url):
            raise HTTPException(
                status_code=400,
                detail="Avatar must be an image URL ending with jpg, jpeg, png, gif, or webp"
            )

    profile = create_or_update_profile(
        db=db,
        user_id=current_user.id,
        full_name=request.full_name,
        bio=request.bio,
        avatar_url=avatar_url
    )

    return {
        "message": "Profile updated successfully",
        "profile": {
            "full_name": profile.full_name,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "updated_at": profile.updated_at,
        }
    }