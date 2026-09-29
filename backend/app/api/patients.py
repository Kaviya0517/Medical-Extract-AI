from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.auth import get_current_user
from app.schemas.extraction import PatientCreate, PatientResponse
from app.database.mongodb import (
    save_patient_db,
    list_patients_db,
    get_patient_db,
    save_activity_log_db,
)

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("/", response_model=PatientResponse)
async def create_patient(payload: PatientCreate, username: str = Depends(get_current_user)):
    patient = await save_patient_db(payload.model_dump())
    await save_activity_log_db(username, "CREATE_PATIENT", f"Registered patient {patient['name']} ({patient['patient_id']})")
    return PatientResponse(**patient)


@router.get("/", response_model=List[PatientResponse])
async def search_patients(
    search: Optional[str] = Query(None, description="Search by ID, Name, or Phone"),
    username: str = Depends(get_current_user),
):
    patients = await list_patients_db(search_term=search)
    return [PatientResponse(**p) for p in patients]


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient_by_id(patient_id: str, username: str = Depends(get_current_user)):
    patient = await get_patient_db(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient record not found")
    return PatientResponse(**patient)
