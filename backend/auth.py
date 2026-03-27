

import bcrypt
from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.database import db
from backend.utils.jwt_handler import verify_access_token


security = HTTPBearer()


def get_role_prefix(role: str) -> str:
    
    prefixes = {
        "care_manager": "CM",
        "parent": "P",
        "child": "C",
    }
    return prefixes[role]



def generate_user_code(role: str) -> str:
   
    prefix = get_role_prefix(role)
    number = 1

    while True:
        code = f"{prefix}{number:03d}"
        existing_user = db.users.find_one({"user_code": code})
        if not existing_user:
            return code
        number += 1



def ensure_user_code(user: dict) -> str:
    
    current_code = user.get("user_code")
    if current_code:
        return current_code

    new_code = generate_user_code(user["role"])
    db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"user_code": new_code}},
    )
    user["user_code"] = new_code
    return new_code



def hash_password(password: str) -> str:
    """
    Hash a plain password before saving it in the database.
    Plain passwords should never be stored.
    """
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")



def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare the login password with the stored hashed password.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )



def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Read the JWT token, verify it, and return the current user.
    This acts like our simple authentication middleware.
    """
    token = credentials.credentials

    try:
        payload = verify_access_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload.",
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token user id.",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    user_code = ensure_user_code(user)

    user["id"] = str(user["_id"])
    user["user_code"] = user_code
    user.pop("_id", None)
    user.pop("password", None)
    return user
