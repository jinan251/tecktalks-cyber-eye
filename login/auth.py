from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from crud import get_user_by_id

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
print("SECRET_KEY:", SECRET_KEY)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user























#load_dotenv()

#SECRET_KEY = os.getenv("SECRET_KEY")
#ALGORITHM = "HS256"
#ACCESS_TOKEN_EXPIRE_MINUTES = 60


#def create_access_token(data: dict):
    #to_encode = data.copy()

    #expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    #to_encode.update({"exp": expire})

    #encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    #return encoded_jwt