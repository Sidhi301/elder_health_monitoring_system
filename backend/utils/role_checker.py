"""
This file contains a simple role checker dependency.
It makes role-based access control easy to reuse in route files.
"""

from fastapi import Depends, HTTPException, status

from backend.auth import get_current_user


def require_role(allowed_roles: list[str]):
    """
    Return a dependency function that checks user roles.
    """

    def role_dependency(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return current_user

    return role_dependency
