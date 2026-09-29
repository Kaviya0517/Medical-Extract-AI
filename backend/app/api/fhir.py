from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from app.api.auth import get_current_user
from app.database.mongodb import get_report_db, list_reports_db

router = APIRouter(prefix="/fhir", tags=["FHIR Compliance"])


@router.get("/Patient/{patient_id}")
async def export_patient_fhir(patient_id: str, username: str = Depends(get_current_user)) -> Dict[str, Any]:
    reports = await list_reports_db(username)
    matching = [r for r in reports if r.get("patient_id") == patient_id]

    if not matching:
        # Fallback to general report if matched
        if reports:
            matching = [reports[0]]
        else:
            raise HTTPException(status_code=404, detail="No clinical records found for FHIR export")

    latest = matching[0]

    fhir_bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": latest.get("patient_id", patient_id),
                    "name": [{"text": latest.get("patient_name") or "Unspecified Patient"}],
                    "gender": (latest.get("gender") or "unknown").lower(),
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": f"enc-{latest.get('id')}",
                    "status": "finished",
                    "class": {"code": latest.get("admission_status", "outpatient").lower()},
                    "subject": {"reference": f"Patient/{latest.get('patient_id')}"},
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": f"cond-{latest.get('id')}",
                    "code": {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/sid/icd-10",
                                "code": latest.get("icd10_code", "R50.9"),
                                "display": ", ".join(latest.get("diagnoses", [])),
                            }
                        ]
                    },
                    "subject": {"reference": f"Patient/{latest.get('patient_id')}"},
                }
            },
        ],
    }

    return fhir_bundle
