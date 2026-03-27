

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt

from backend.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY


ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
   
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> dict:
    
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
