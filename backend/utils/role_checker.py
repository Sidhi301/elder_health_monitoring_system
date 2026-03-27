

from fastapi import Depends, HTTPException, status

from backend.auth import get_current_user


def require_role(allowed_roles: list[str]):
  

    def role_dependency(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return current_user

    return role_dependency
