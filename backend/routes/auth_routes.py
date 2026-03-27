

from fastapi import APIRouter, HTTPException, status

from backend.auth import ensure_user_code, generate_user_code, hash_password, verify_password
from backend.config import CARE_MANAGER_SECRET
from backend.database import db
from backend.models import UserLogin, UserRegister
from backend.utils.jwt_handler import create_access_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register_user(user: UserRegister):
  
    existing_user = db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    if user.role == "care_manager" and user.care_manager_secret != CARE_MANAGER_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Care Manager secret.",
        )

    user_data = user.model_dump()
    user_data.pop("care_manager_secret", None)
    user_data["password"] = hash_password(user.password)
    user_data["user_code"] = generate_user_code(user.role)
    result = db.users.insert_one(user_data)

    return {
        "message": "User registered successfully.",
        "user_id": str(result.inserted_id),
        "user_code": user_data["user_code"],
        "role": user.role,
    }


@router.post("/login")
def login_user(user: UserLogin):
   
    existing_user = db.users.find_one({"email": user.email})
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(user.password, existing_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    user_code = ensure_user_code(existing_user)

    access_token = create_access_token(
        {
            "user_id": str(existing_user["_id"]),
            "email": existing_user["email"],
            "role": existing_user["role"],
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(existing_user["_id"]),
            "user_code": user_code,
            "name": existing_user["name"],
            "email": existing_user["email"],
            "role": existing_user["role"],
        },
    }
