

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from backend.database import db
from backend.models import EmergencyCreate, HealthRecordCreate, PatientCreate
from backend.utils.role_checker import require_role


router = APIRouter(prefix="/api", tags=["Health"])


def generate_patient_code() -> str:
    
    number = 1

    while True:
        code = f"PT{number:03d}"
        existing_patient = db.patients.find_one({"patient_code": code})
        if not existing_patient:
            return code
        number += 1


def get_patient_by_code(patient_code: str) -> dict | None:
   
    return db.patients.find_one({"patient_code": patient_code})


def create_alerts_from_health_data(health_data: HealthRecordCreate) -> list[dict]:
    
    alerts = []
    current_time = datetime.now(timezone.utc)

    if health_data.heart_rate < 50 or health_data.heart_rate > 110:
        alerts.append(
            {
                "patient_id": health_data.patient_id,
                "message": f"Heart rate alert: {health_data.heart_rate} bpm",
                "severity": "warning",
                "created_at": current_time,
            }
        )

    if health_data.oxygen_level < 92:
        alerts.append(
            {
                "patient_id": health_data.patient_id,
                "message": f"Critical oxygen level: {health_data.oxygen_level}%",
                "severity": "critical",
                "created_at": current_time,
            }
        )

    if health_data.systolic_bp > 140 or health_data.diastolic_bp > 90:
        alerts.append(
            {
                "patient_id": health_data.patient_id,
                "message": (
                    "Blood pressure warning: "
                    f"{health_data.systolic_bp}/{health_data.diastolic_bp} mmHg"
                ),
                "severity": "warning",
                "created_at": current_time,
            }
        )

    return alerts


@router.get("/patients")
def get_patients(
    current_user: dict = Depends(require_role(["care_manager", "parent", "child"])),
):
    
    if current_user["role"] == "care_manager":
        patients = list(db.patients.find({"care_manager_user_code": current_user["user_code"]}))
    elif current_user["role"] == "parent":
        patients = list(db.patients.find({"parent_user_code": current_user["user_code"]}))
    else:
        patients = list(db.patients.find({"child_user_code": current_user["user_code"]}))

    for patient in patients:
        patient["id"] = str(patient["_id"])
        patient.pop("_id", None)

    return {"patients": patients}


@router.post("/patients")
def create_patient(
    patient: PatientCreate,
    current_user: dict = Depends(require_role(["care_manager"])),
):
   
    parent_user = db.users.find_one({"user_code": patient.parent_user_code})
    child_user = None

    if not parent_user or parent_user["role"] != "parent":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent user code is invalid.",
        )

    if patient.child_user_code:
        child_user = db.users.find_one({"user_code": patient.child_user_code})
        if not child_user or child_user["role"] != "child":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Child user code is invalid.",
            )

    patient_data = patient.model_dump()
    patient_data["patient_code"] = generate_patient_code()
    patient_data["care_manager_user_code"] = current_user["user_code"]
    patient_data["care_manager_name"] = current_user["name"]
    result = db.patients.insert_one(patient_data)

    return {
        "message": "Patient created successfully.",
        "patient_id": patient_data["patient_code"],
        "patient_code": patient_data["patient_code"],
    }


@router.post("/health")
def add_health_record(
    health_data: HealthRecordCreate,
    current_user: dict = Depends(require_role(["care_manager"])),
):
   
    patient = get_patient_by_code(health_data.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    record_data = health_data.model_dump()
    record_data["patient_name"] = patient["name"]
    record_data["added_by"] = current_user["user_code"]
    record_data["created_at"] = datetime.now(timezone.utc)
    result = db.health_records.insert_one(record_data)

    alerts = create_alerts_from_health_data(health_data)
    if alerts:
        db.alerts.insert_many(alerts)

    return {
        "message": "Health record added successfully.",
        "record_id": str(result.inserted_id),
        "alerts_created": len(alerts),
    }


@router.get("/patient/{patient_id}")
def get_patient_data(
    patient_id: str,
    current_user: dict = Depends(require_role(["care_manager", "parent", "child"])),
):
   
    patient = get_patient_by_code(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    current_role = current_user["role"]
    allowed = False

    if current_role == "care_manager" and patient["care_manager_user_code"] == current_user["user_code"]:
        allowed = True
    if current_role == "parent" and patient["parent_user_code"] == current_user["user_code"]:
        allowed = True
    if current_role == "child" and patient.get("child_user_code") == current_user["user_code"]:
        allowed = True

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot view this patient data.",
        )

    health_records = list(
        db.health_records.find({"patient_id": patient_id}).sort("created_at", -1)
    )

    patient["id"] = str(patient["_id"])
    patient.pop("_id", None)

    for record in health_records:
        record["id"] = str(record["_id"])
        record.pop("_id", None)

    return {"patient": patient, "health_records": health_records}


@router.post("/emergency")
def send_emergency_alert(
    emergency: EmergencyCreate,
    current_user: dict = Depends(require_role(["parent"])),
):
   
    patient = get_patient_by_code(emergency.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    if patient["parent_user_code"] != current_user["user_code"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only send emergency alerts for your linked patient.",
        )

    alert_data = {
        "patient_id": emergency.patient_id,
        "message": f"Emergency: {emergency.message}",
        "severity": "emergency",
        "created_at": datetime.now(timezone.utc),
        "created_by": current_user["user_code"],
    }
    result = db.alerts.insert_one(alert_data)

    return {
        "message": "Emergency alert sent successfully.",
        "alert_id": str(result.inserted_id),
    }
