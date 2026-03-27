"""
This file contains all Pydantic models used for request validation.
Keeping models in one file makes the project easier to explain.
"""

from datetime import datetime
from typing import Optional, Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field


RoleType = Literal["care_manager", "parent", "child"]


class UserRegister(BaseModel):
    """
    Data needed to register a new user.
    Care Manager registration can also include a secret code.
    """

    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: RoleType
    care_manager_secret: Optional[str] = Field(default="", max_length=100)


class UserLogin(BaseModel):
    """
    Data needed for user login.
    """

    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class PatientCreate(BaseModel):
    """
    Care Manager can create a patient record with linked user codes.
    Older field names are also accepted to avoid frontend cache issues.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=1, le=120)
    parent_user_code: str = Field(
        ...,
        min_length=2,
        max_length=20,
        validation_alias=AliasChoices("parent_user_code", "parentUserCode", "parent_user_id"),
    )
    child_user_code: Optional[str] = Field(
        default=None,
        max_length=20,
        validation_alias=AliasChoices("child_user_code", "childUserCode", "child_user_id"),
    )


class HealthRecordCreate(BaseModel):
    """
    Health data submitted by a Care Manager.
    """

    patient_id: str = Field(..., min_length=2, max_length=20)
    heart_rate: int = Field(..., ge=20, le=250)
    oxygen_level: int = Field(..., ge=50, le=100)
    systolic_bp: int = Field(..., ge=60, le=250)
    diastolic_bp: int = Field(..., ge=40, le=180)
    notes: Optional[str] = Field(default="", max_length=300)


class EmergencyCreate(BaseModel):
    """
    Parent can send an emergency message for urgent help.
    """

    patient_id: str = Field(..., min_length=2, max_length=20)
    message: str = Field(..., min_length=3, max_length=300)


class AlertCreate(BaseModel):
    """
    Internal model used when the system creates an alert.
    """

    patient_id: str
    message: str
    severity: Literal["warning", "critical", "emergency"]
    created_at: datetime
