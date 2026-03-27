

from fastapi import APIRouter, Depends

from backend.database import db
from backend.utils.role_checker import require_role


router = APIRouter(prefix="/api", tags=["Alerts"])


@router.get("/alerts")
def get_alerts(current_user: dict = Depends(require_role(["care_manager", "parent", "child"]))):
   
    user_role = current_user["role"]

    if user_role == "care_manager":
        patients = list(db.patients.find({"care_manager_user_code": current_user["user_code"]}))
    elif user_role == "parent":
        patients = list(db.patients.find({"parent_user_code": current_user["user_code"]}))
    else:
        patients = list(db.patients.find({"child_user_code": current_user["user_code"]}))

    patient_ids = [patient["patient_code"] for patient in patients]
    alerts = list(db.alerts.find({"patient_id": {"$in": patient_ids}}).sort("created_at", -1))

    for alert in alerts:
        alert["id"] = str(alert["_id"])
        alert.pop("_id", None)

    return {"alerts": alerts}
