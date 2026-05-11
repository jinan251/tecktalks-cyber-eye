import re
from fastapi import HTTPException

def validate_username(username: str):
    reserved_names = {"admin", "root", "support", "moderator", "system"}

    if len(username) < 3 or len(username) > 20:
        raise HTTPException(
            status_code=400,
            detail="Username must be between 3 and 20 characters"
        )

    if not re.fullmatch(r"[A-Za-z0-9_]+", username):
        raise HTTPException(
            status_code=400,
            detail="Username can only contain letters, numbers, and underscores"
        )

    if username.lower() in reserved_names:
        raise HTTPException(
            status_code=400,
            detail="This username is not allowed"
        )